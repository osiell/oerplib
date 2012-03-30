# -*- coding: UTF-8 -*-
"""This module provides the OSV class."""

import collections
import ast

from oerplib import error
from oerplib.service.osv import fields, browse


class OSV(collections.Mapping):
    """Represent a data model from the `OpenERP` server."""

    fields_reserved = ['id', '__oerp__', '__osv__', '__data__']
    def __init__(self, oerp, osv_name):
        super(OSV, self).__init__()
        self._oerp = oerp
        self._browse_class = self._generate_browse_class(osv_name)

    def browse(self, obj_id, context=None):
        """Generate an instance of the OSV class (called 'browse_record')."""
        obj = self._browse_class(obj_id)
        self._refresh(obj, context)
        return obj

    def _generate_browse_class(self, osv_name):
        """Generate a class with all its fields corresponding to
        the OSV name supplied and return them.

        """
        # Retrieve server fields info and generate corresponding local fields
        #FIXME try catch needed?
        try:
            fields_get = self._oerp.execute(osv_name, 'fields_get')
        except error.RPCError:
            raise error.RPCError(
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
        cls.__oerp__ = self._oerp
        cls.__osv__ = {'name': osv_name, 'columns': cls_fields}
        slots = ['__oerp__', '__osv__', '__dict__', '__data__']
        slots.extend(cls_fields.keys())
        cls.__slots__ = slots
        return cls

    def _write_record(self, obj, context=None):
        """Send values of fields updated to the OpenERP server."""
        obj_data = obj.__data__
        vals = {}
        for field_name in obj_data['fields_updated']:
            if field_name in obj_data['raw_data']:
                field = self._browse_class.__osv__['columns'][field_name]
                # Many2One fields
                if isinstance(field, fields.Many2OneField):
                    vals[field_name] = getattr(obj,
                                               "_{0}".format(field_name))[0]
                # One2Many fields
                #elif isinstance(field, fields.One2ManyField):
                #    print field.relation
                #    for rel_id in getattr(obj, "_{0}".format(field_name)):
                #        self._oerp.write(field.relation, rel_id,
                #                        {'??FIELD??': obj.id})
                #    #vals[field_name] = getattr(obj, "_{0}".format(field_name))
                # Many2Many fields
                elif isinstance(field, fields.Many2ManyField):
                    pass #TODO write Many2Many value
                # All other fields
                else:
                    vals[field_name] = getattr(obj, "_{0}".format(field_name))
        try:
            res = self._oerp.write(obj.__osv__['name'], [obj.id], vals, context)
        except error.Error as exc:
            raise exc
        else:
            # Update raw_data dictionary
            self._refresh(obj, context) #FIXME delete to avoid a RPC request?
            return res

    def _refresh(self, obj, context=None):
        """Retrieve field values from OpenERP server.
        May be used to restore the original values
        in the purpose to cancel all changes made.

        """
        obj_data = obj.__data__
        obj_data['raw_data'] = self._oerp.read(obj.__osv__['name'], obj.id)
        if obj_data['raw_data'] is False:
            raise error.RPCError(
                u"There is no '{osv_name}' record with ID {obj_id}.".format(
                    osv_name=obj.__class__.__osv__['name'], obj_id=obj.id))
        # Special field 'name' have to be filled with the value returned
        # by the 'name_get' method
        #try:
        #    name = self._oerp.execute(obj.__osv__['name'], 'name_get', [obj.id])
        #except error.Error:
        #    pass
        #else:
        #    if name:
        #        try:
        #            obj_data['raw_data']['name'] = ast.literal_eval(name[0][1])
        #        except Exception:
        #            obj_data['raw_data']['name'] = name[0][1]
        self._reset(obj)

    def _reset(self, obj):
        """Cancel all changes by restoring field values with original values
        obtained during the last refresh (object instanciation or
        last call to _refresh() method).

        """
        obj_data = obj.__data__
        obj_data['fields_updated'] = []
        # Load fields and their values
        for field in self._browse_class.__osv__['columns'].values():
            if field.name in obj_data['raw_data']:
                setattr(obj, "_{0}".format(field.name),
                        obj_data['raw_data'][field.name])
                setattr(obj.__class__, field.name,
                        field)

    def _unlink_record(self, obj, context=None):
        """Delete the object from the OpenERP server."""
        return self._oerp.unlink(obj.__osv__, [obj.id], context)

    def __getattr__(self, method):
        def rpc_method(*args):
            result = self._oerp.execute(self._browse_class.__osv__['name'],
                                        method, *args)
            return result
        return rpc_method

    # ---------------------------- #
    # -- MutableMapping methods -- #
    # ---------------------------- #

    def __getitem__(self, obj_id):
        return self.browse(obj_id)

    def __iter__(self):
        ids = self._oerp.search(self._browse_class.__osv__['name'])
        for obj_id in ids:
            yield self.browse(obj_id)

    def __len__(self):
        return self._oerp.search(self._browse_class.__osv__['name'], count=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
