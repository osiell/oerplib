# -*- coding: UTF-8 -*-
"""This module provides the OSV class
and some functions to manipulate its instances.
"""
import collections
from oerplib import error, fields


class OSV(object):
    """Base class that all OSV classes inherit from."""
    def __init__(self, factory, o_id):
        self.id = o_id
        factory.refresh(self)

fields.OSV_CLASS = OSV


class Factory(collections.MutableMapping):
    """Manage the objects corresponding to a OSV class."""

    fields_reserved = ['id', 'oerp']
    def __init__(self, oerp, osv_name):
        super(Factory, self).__init__()
        self.oerp = oerp
        self.osv = {
            'name': osv_name,
            'class': None,
            'fields': {},
        }
        self.osv['class'] = self.generate_osv(osv_name)
        self.objects = {}

    def generate_browse(self, obj_id, join=False, refresh=False):
        """Generate an instance of the OSV class."""
        # TODO be able to refresh all joined relations
        if obj_id not in self.objects or refresh:
            self.objects[obj_id] = {
                'raw_data': None,
                'fields_updated': [],
                'instance': None,
                'join': join,
            }
            try:
                self.objects[obj_id]['instance'] = self.osv['class'](self, obj_id)
            except error.ExecuteQueryError as exc:
                del self.objects[obj_id]
                raise error.ExecuteQueryError(
                    u"There is no '{0}' record with ID {1}.".format(
                        self.osv['name'], obj_id))

        return self.objects[obj_id]['instance']

    def generate_osv(self, osv_name):
        """Generate a class (with all its fields)
        corresponding to the OSV name supplied.

        """
        try:
            fields_get = self.oerp.execute(osv_name, 'fields_get')
        except error.ExecuteQueryError as exc:
            raise error.ExecuteQueryError(
                u"There is no OSV class named '{0}'.".format(self.osv['name']))
        cls_name = osv_name.replace('.', '_')
        for field_name, field_data in fields_get.items():
            if field_name not in self.fields_reserved:
                self.osv['fields'][field_name] = fields.generate_field(
                                                            self,
                                                            field_name,
                                                            field_data)
        cls = type(cls_name, (OSV,), {})
        cls._oerp = self.oerp
        return cls

    def write(self, obj):
        """Send values of fields updated to the OpenERP server."""
        obj_info = self.objects[obj.id]
        vals = {}
        for field_name in obj_info['fields_updated']:
            if field_name in obj_info['raw_data']:
                field = self.osv['fields'][field_name]
                # Many2One fields
                if isinstance(field, fields.Many2OneField):
                    vals[field_name] = getattr(obj,
                                               "_{0}".format(field_name))[0]
                # One2Many fields
                elif isinstance(field, fields.One2ManyField):
                    pass #TODO write One2Many value
                # Many2Many fields
                elif isinstance(field, fields.Many2ManyField):
                    pass #TODO write Many2Many value
                # All other fields
                else:
                    vals[field_name] = getattr(obj, "_{0}".format(field_name))
        try:
            res = self.oerp.write(self.osv['name'], [obj.id], vals)
        except error.Error as exc:
            raise
        else:
            # Update raw_data dictionary
            self.refresh(obj)
            return res

    def refresh(self, obj):
        """Retrieve field values from OpenERP server.
        May be used to restore the original values
        in the purpose to cancel all changes made.

        """
        obj_info = self.objects[obj.id]
        obj_info['raw_data'] = self.oerp.read(self.osv['name'], obj.id)
        self.reset(obj)

    def reset(self, obj):
        """Cancel all changes by restoring field values with original values
        obtained during the last refresh (object instanciation or
        last call to refresh() method).

        """
        obj_info = self.objects[obj.id]
        obj_info['fields_updated'] = []
        # Load fields
        for field in self.osv['fields'].values():
            if field.name in obj_info['raw_data']:
                setattr(obj, "_{0}".format(field.name),
                        obj_info['raw_data'][field.name])
                setattr(obj.__class__, field.name,
                        field.get_property())
                # Preload value (for relation fields as One2Many, Many2One...)
                if obj_info['join']:
                    getattr(obj, field.name)

    def unlink(self, obj):
        """Delete the object locally and from the server."""
        #TODO delete locally
        return self.oerp.unlink(self.osv['name'], [obj.id])

    def __str__(self):
        """Return string representation of this factory."""
        return str([obj_id for obj_id in self.objects.keys()])

    # ---------------------------- #
    # -- MutableMapping methods -- #
    # ---------------------------- #

    def __delitem__(self, obj_id):
        del self.objects[obj_id]
        #raise error.NotAllowedError(u"Operation not supported")

    def __getitem__(self, obj_id):
        return self.generate_browse(obj_id)

    def __iter__(self):
        for obj_id in self.objects:
            yield obj_id

    def __len__(self):
        return len(self.objects)

    def __setitem__(self, key, value):
        raise error.NotAllowedError(u"Operation not supported")

