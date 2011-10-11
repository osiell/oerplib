# -*- coding: UTF-8 -*-
"""This module provides the OSV class
and some functions to manipulate its instances.
"""
import collections
import ast

from oerplib import error, fields


class OSV(object):
    """Base class that all OSV classes inherit from.
    No attributes should be defined in this class (except _id/id and
    Python magic methods) in order to not be conflicted with the fields
    defined in the OSV-base class on OpenERP server.

    """
    def __init__(self, factory, o_id):
        self._id = o_id

        # Define __str__ and __repr__ methods
        #NOTE: this is made in this way because the 'factory' variable
        # can't be accessed through another way
        def __str__(self):
            return "browse_record({osv_name}, {obj_id})".format(
                    osv_name=factory.osv['name'], obj_id=self._id)
        self.__class__.__str__ = __str__
        self.__class__.__repr__ = __str__

    @property
    def id(self):
        return self._id

fields.OSV_CLASS = OSV


def check_obj(func):
    """Decorator to check the availability of the object."""
    def wrapper(self, obj):
        if obj.id not in self.objects:
            raise ValueError("This object is no longer referenced,"
                             " operation canceled.")
        return func(self, obj)
    return wrapper


class Factory(collections.MutableMapping):
    """Manage the objects corresponding to an OSV class."""

    fields_reserved = ['id', 'oerp']
    def __init__(self, oerp, osv_name):
        super(Factory, self).__init__()
        self.oerp = oerp
        self.osv = {'name': osv_name}
        self.osv['class'], self.osv['fields'] = self._generate_osv_class()
        self.objects = {}

    def generate_browse_record(self, obj_id, refresh=True):
        """Generate an instance of the OSV class."""
        if obj_id not in self.objects:
            self.objects[obj_id] = {}
            try:
                self.objects[obj_id]['instance'] = self.osv['class'](self,
                                                                     obj_id)
            except error.ExecuteQueryError as exc:
                del self.objects[obj_id]
                raise error.ExecuteQueryError(
                    u"There is no '{osv_name}' record with ID {obj_id}.".format(
                        osv_name=self.osv['name'], obj_id=obj_id))
        if refresh:
            self.refresh(self.objects[obj_id]['instance'])
        return self.objects[obj_id]['instance']

    def _generate_osv_class(self):
        """Generate a class with all its fields corresponding to
        the OSV name supplied and return them.

        """
        # Retrieve server fields info and generate corresponding local fields
        try:
            fields_get = self.oerp.execute(self.osv['name'], 'fields_get')
        except error.ExecuteQueryError as exc:
            raise error.ExecuteQueryError(
                u"There is no OSV class named '{0}'.".format(self.osv['name']))
        cls_name = self.osv['name'].replace('.', '_')
        cls_fields = {}
        for field_name, field_data in fields_get.items():
            if field_name not in Factory.fields_reserved:
               cls_fields[field_name] = fields.generate_field(self,
                                                              field_name,
                                                              field_data)
        # Case where no field 'name' exists, we generate one (which will be
        # in readonly mode) in purpose to be filled with the 'name_get' method
        if 'name' not in cls_fields:
            field_data = {'type': 'text', 'string': 'Name', 'readonly': True}
            cls_fields['name'] = fields.generate_field(self, 'name', field_data)

        cls = type(cls_name, (OSV,), {})
        cls.__oerp__ = self.oerp
        return cls, cls_fields

    @check_obj
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
            res = self.oerp.write(self.osv['name'], [obj.id], vals)
        except error.Error as exc:
            raise
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
        obj_info = self.objects[obj.id]
        obj_info['raw_data'] = self.oerp.read(self.osv['name'], obj.id)
        # Special field 'name' have to be filled with the value returned
        # by the 'name_get' method
        try:
            name = self.oerp.execute(self.osv['name'], 'name_get', obj.id)
        except Exception as exc:
            pass
        else:
            if name:
                try:
                    obj_info['raw_data']['name'] = ast.literal_eval(name[0][1])
                except:
                    obj_info['raw_data']['name'] = name[0][1]
        self.reset(obj)

    @check_obj
    def reset(self, obj):
        """Cancel all changes by restoring field values with original values
        obtained during the last refresh (object instanciation or
        last call to refresh(obj) method).

        """
        obj_info = self.objects[obj.id]
        obj_info['fields_updated'] = []
        # Load fields and their values
        for field in self.osv['fields'].values():
            if field.name in obj_info['raw_data']:
                setattr(obj, "_{0}".format(field.name),
                        obj_info['raw_data'][field.name])
                setattr(obj.__class__, field.name,
                        field.get_property())

    @check_obj
    def unlink(self, obj):
        """Delete the object locally and from the server."""
        del self.objects[obj.id]
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
        return self.generate_browse_record(obj_id)

    def __iter__(self):
        for obj_id in self.objects:
            yield obj_id
            #yield self.objects[obj_id]

    def __len__(self):
        return len(self.objects)

    def __setitem__(self, key, value):
        raise error.NotAllowedError(u"Operation not supported")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
