# -*- coding: UTF-8 -*-
"""This module provides the OSV class."""

import collections
import ast

from oerplib import error, fields, browse


def check_obj(func):
    """Decorator to check the availability of the object."""
    def wrapper(self, obj):
        if obj.id not in self.browse_records:
            raise ValueError("This object is no longer referenced,"
                             " operation canceled.")
        return func(self, obj)
    return wrapper


class OSV(collections.MutableMapping):
    """Manage the objects corresponding to an OSV class."""

    fields_reserved = ['id', '__oerp__', '__osv__']
    def __init__(self, oerp, osv_name):
        super(OSV, self).__init__()
        self.oerp = oerp
        self.browse_records = {}
        self.browse_class = self._generate_browse_class(osv_name)

    def browse(self, obj_id, refresh=True):
        """Generate an instance of the OSV class (called 'browse_record')."""
        if obj_id not in self.browse_records:
            self.browse_records[obj_id] = {}
            self.browse_records[obj_id]['instance'] = self.browse_class(obj_id)
        if refresh:
            self.refresh(self.browse_records[obj_id]['instance'])
        return self.browse_records[obj_id]['instance']

    def _generate_browse_class(self, osv_name):
        """Generate a class with all its fields corresponding to
        the OSV name supplied and return them.

        """
        # Retrieve server fields info and generate corresponding local fields
        try:
            fields_get = self.oerp.execute(osv_name, 'fields_get')
        except error.ExecuteQueryError:
            raise error.ExecuteQueryError(
                u"There is no OSV class named '{0}'.".format(osv_name))
        cls_name = osv_name.replace('.', '_')
        cls_fields = {}
        for field_name, field_data in fields_get.items():
            if field_name not in OSV.fields_reserved:
                cls_fields[field_name] = fields.generate_field(self,
                                                               field_name,
                                                               field_data)
        # Case where no field 'name' exists, we generate one (which will be
        # in readonly mode) in purpose to be filled with the 'name_get' method
        if 'name' not in cls_fields:
            field_data = {'type': 'text', 'string': 'Name', 'readonly': True}
            cls_fields['name'] = fields.generate_field(self, 'name', field_data)

        cls = type(cls_name, (browse.BrowseRecord,), {})
        cls.__oerp__ = self.oerp
        cls.__osv__ = {'name': osv_name, 'columns': cls_fields}
        slots = ['__oerp__', '__osv__', '__dict__']
        slots.extend(cls_fields.keys())
        cls.__slots__ = slots
        return cls

    @check_obj
    def write(self, obj):
        """Send values of fields updated to the OpenERP server."""
        obj_info = self.browse_records[obj.id]
        vals = {}
        for field_name in obj_info['fields_updated']:
            if field_name in obj_info['raw_data']:
                field = self.browse_class.__osv__['columns'][field_name]
                # Many2One fields
                if isinstance(field, fields.Many2OneField):
                    vals[field_name] = getattr(obj,
                                               "_{0}".format(field_name))[0]
                # One2Many fields
                #elif isinstance(field, fields.One2ManyField):
                #    print field.relation
                #    for rel_id in getattr(obj, "_{0}".format(field_name)):
                #        self.oerp.write(field.relation, rel_id,
                #                        {'??FIELD??': obj.id})
                #    #vals[field_name] = getattr(obj, "_{0}".format(field_name))
                # Many2Many fields
                elif isinstance(field, fields.Many2ManyField):
                    pass #TODO write Many2Many value
                # All other fields
                else:
                    vals[field_name] = getattr(obj, "_{0}".format(field_name))
        try:
            res = self.oerp.write(obj.__osv__['name'], [obj.id], vals)
        except error.Error as exc:
            raise exc
        else:
            # Update raw_data dictionary
            self.refresh(obj)
            return res

    @check_obj
    def refresh(self, obj):
        """Retrieve field values from OpenERP server.
        May be used to restore the original values
        in the purpose to cancel all changes made.

        """
        obj_info = self.browse_records[obj.id]
        obj_info['raw_data'] = self.oerp.read(obj.__osv__['name'], obj.id)
        if obj_info['raw_data'] is False:
            raise error.ExecuteQueryError(
                u"There is no '{osv_name}' record with ID {obj_id}.".format(
                    osv_name=obj.__class__.__osv__['name'], obj_id=obj.id))
        # Special field 'name' have to be filled with the value returned
        # by the 'name_get' method
        try:
            name = self.oerp.execute(obj.__osv__['name'], 'name_get', [obj.id])
        except error.Error:
            pass
        else:
            if name:
                try:
                    obj_info['raw_data']['name'] = ast.literal_eval(name[0][1])
                except Exception:
                    obj_info['raw_data']['name'] = name[0][1]
        self.reset(obj)

    @check_obj
    def reset(self, obj):
        """Cancel all changes by restoring field values with original values
        obtained during the last refresh (object instanciation or
        last call to refresh(obj) method).

        """
        obj_info = self.browse_records[obj.id]
        obj_info['fields_updated'] = []
        # Load fields and their values
        for field in self.browse_class.__osv__['columns'].values():
            if field.name in obj_info['raw_data']:
                setattr(obj, "_{0}".format(field.name),
                        obj_info['raw_data'][field.name])
                setattr(obj.__class__, field.name,
                        field)

    @check_obj
    def unlink(self, obj):
        """Delete the object locally and from the server."""
        del self.browse_records[obj.id]
        return self.oerp.unlink(obj.__osv__, [obj.id])

    def __str__(self):
        """Return string representation of this OSV class."""
        return str([obj_id for obj_id in self.browse_records.keys()])

    # ---------------------------- #
    # -- MutableMapping methods -- #
    # ---------------------------- #

    def __delitem__(self, obj_id):
        del self.browse_records[obj_id]
        #raise error.NotAllowedError(u"Operation not supported")

    def __getitem__(self, obj_id):
        return self.browse(obj_id)

    def __iter__(self):
        for obj_id in self.browse_records:
            yield obj_id
            #yield self.browse_records[obj_id]

    def __len__(self):
        return len(self.browse_records)

    def __setitem__(self, key, value):
        raise error.NotAllowedError(u"Operation not supported")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
