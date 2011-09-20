# -*- coding: UTF-8 -*-
"""This module contains classes representing the fields supported by OpenObject.
"""
import datetime

from oerplib import error
OSV_CLASS = None


class BaseField(object):
    """Field which all other fields inherit.
    Manage common metadata.
    """
    def __init__(self, factory, name, data):
        self.factory = factory
        self.name = name
        self.type = 'type' in data and data['type'] or False
        self.string = 'string' in data and data['string'] or False
        self.size = 'size' in data and data['size'] or False
        self.required = 'required' in data and data['required'] or False
        self.readonly = 'readonly' in data and data['readonly'] or False
        self.help = 'help' in data and data['help'] or False
        self.states = 'states' in data and data['states'] or False

    def get_property(self):
        """Generate a Python class property corresponding to the field type."""
        pass

    def check_value(self, value):
        """Check the validity of a value for the field."""
        if self.readonly:
            raise error.NotAllowedError(
                u"'{field_name}' field is readonly".format(
                    field_name=self.name))
        if self.size and len(value) > self.size:
            raise error.NotAllowedError(
                u"Lenght of the '{field_name}' is limited to {size}".format(
                    field_name=self.name,
                    size=self.size))
        if not value and self.required:
            raise error.NotAllowedError(
                u"'{field_name}' field require a value".format(
                    field_name=self.name))
        return value


class SelectionField(BaseField):
    """Represent the OpenObject 'fields.selection'"""
    def __init__(self, factory, name, data):
        super(SelectionField, self).__init__(factory, name, data)
        self.selection = 'selection' in data and data['selection'] or False

    def get_property(self):
        def getter(obj):
            return getattr(obj, "_{0}".format(self.name))

        def setter(obj, value):
            value = self.check_value(value)
            setattr(obj, "_{0}".format(self.name), value)
            self.factory.objects[obj.id]['fields_updated'].append(self.name)

        return property(getter, setter)

    def check_value(self, value):
        super(SelectionField, self).check_value(value)
        selection = [val[0] for val in self.selection]
        if value not in selection:
            raise error.NotAllowedError(
                u"The value '{value}' supplied doesn't match with the possible \
values '{selection}' for the '{field_name}' field".format(
                    value=value,
                    selection=selection,
                    field_name=self.name,
            ))
        return value


class Many2ManyField(BaseField):
    """Represent the OpenObject 'fields.many2many'"""
    def __init__(self, factory, name, data):
        super(Many2ManyField, self).__init__(factory, name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or False
        self.domain = 'domain' in data and data['domain'] or False

    def get_property(self):
        def getter(obj):
            return [self.factory.oerp.browse(self.relation, o_id) 
                    for o_id in self.factory.objects[obj.id]['raw_data'][self.name]]

        def setter(obj, value):
            raise error.NotAllowedError(u"Not implemented yet")

        return property(getter, setter)

    def check_value(self, value):
        #TODO Many2Many.check_value()
        super(Many2ManyField, self).check_value(value)

class Many2OneField(BaseField):
    """Represent the OpenObject 'fields.many2one'"""
    def __init__(self, factory, name, data):
        super(Many2OneField, self).__init__(factory, name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or False
        self.domain = 'domain' in data and data['domain'] or False

    def get_property(self):
        def is_int(value):
            try:
                int(value)
                return True
            except Exception as exc:
                return False

        def getter(obj):
            if getattr(obj, "_{0}".format(self.name)):
                return obj.__class__._oerp.browse(
                    self.relation,
                    getattr(obj, "_{0}".format(self.name))[0]
                )

        def setter(obj, value):
            if isinstance(value, OSV_CLASS):
                o_rel = value
            if is_int(value):
                o_rel = obj.__class__._oerp.browse(self.relation, value)
            o_rel = self.check_value(o_rel)
            setattr(obj, "_{0}".format(self.name), [o_rel.id, o_rel.name])
            self.factory.objects[obj.id]['fields_updated'].append(self.name)

        return property(getter, setter)

    def check_value(self, value):
        super(Many2OneField, self).check_value(value)
        oerp = self.factory.oerp
        value_factory = oerp.pool.get_by_class(value.__class__)
        if value_factory.osv['name'] != self.relation:
            raise error.NotAllowedError(
                (u"Instance of '{osv_name}' supplied doesn't match with the " +\
                u"relation '{relation}' of the '{field_name}' field.").format(
                    osv_name=value_factory.osv['name'],
                    relation=self.relation,
                    field_name=self.name))
        return value

class One2ManyField(BaseField):
    """Represent the OpenObject 'fields.one2many'"""
    def __init__(self, factory, name, data):
        super(One2ManyField, self).__init__(factory, name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or False
        self.domain = 'domain' in data and data['domain'] or False

    def get_property(self):
        def getter(obj):
            return [self.factory.oerp.browse(self.relation, o_id) 
                    for o_id in self.factory.objects[obj.id]['raw_data'][self.name]]

        def setter(obj, value):
            #TODO: setter of One2Many field
            raise error.NotAllowedError(u"Not implemented yet")

        return property(getter, setter)

    def check_value(self, value):
        #TODO One2Many.check_value()
        super(One2ManyField, self).check_value(value)


class DateField(BaseField):
    """Represent the OpenObject 'fields.data'"""
    pattern = "%Y-%m-%d"
    def __init__(self, factory, name, data):
        super(DateField, self).__init__(factory, name, data)

    def get_property(self):
        def getter(obj):
            value = getattr(obj, "_{0}".format(self.name))
            try:
                res = datetime.datetime.strptime(value, self.pattern).date()
            except Exception:
                res = value
            return res

        def setter(obj, value):
            value = self.check_value(value)
            setattr(obj, "_{0}".format(self.name), value)
            self.factory.objects[obj.id]['fields_updated'].append(self.name)

        return property(getter, setter)

    def check_value(self, value):
        super(DateField, self).check_value(value)
        if isinstance(value, datetime.date):
            value = value.strftime("%Y-%m-%d")
        elif isinstance(value, basestring):
            try:
                datetime.datetime.strptime(value, self.pattern)
            except:
                raise ValueError(
                    "Value not well formatted, expecting '{0}' format".format(
                        self.pattern))
        else:
            raise ValueError("Expecting a datetime.date object or basestring")
        return value


class DateTimeField(BaseField):
    """Represent the OpenObject 'fields.datetime'"""
    pattern = "%Y-%m-%d %H:%M:%S"
    def __init__(self, factory, name, data):
        super(DateTimeField, self).__init__(factory, name, data)

    def get_property(self):
        def getter(obj):
            value = getattr(obj, "_{0}".format(self.name))
            try:
                res = datetime.datetime.strptime(value, self.pattern)
            except Exception:
                res = value
            return res

        def setter(obj, value):
            value = self.check_value(value)
            setattr(obj, "_{0}".format(self.name), value)
            self.factory.objects[obj.id]['fields_updated'].append(self.name)

        return property(getter, setter)

    def check_value(self, value):
        super(DateTimeField, self).check_value(value)
        if isinstance(value, datetime.datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, basestring):
            try:
                datetime.datetime.strptime(value, self.pattern)
            except:
                raise ValueError(
                    "Value not well formatted, expecting '{0}' format".format(
                        self.pattern))
        else:
            raise ValueError(
                "Expecting a datetime.datetime object or basestring")
        return value


class ValueField(BaseField):
    """Represent simple OpenObject fields:
    - 'fields.char',
    - 'fields.float',
    - 'fields.integer',
    - 'fields.boolean',
    - 'fields.text',
    - 'fields.binary',
    """
    def __init__(self, factory, name, data):
        super(ValueField, self).__init__(factory, name, data)

    def get_property(self):
        def getter(obj):
            return getattr(obj, "_{0}".format(self.name))

        def setter(obj, value):
            value = self.check_value(value)
            setattr(obj, "_{0}".format(self.name), value)
            self.factory.objects[obj.id]['fields_updated'].append(self.name)

        return property(getter, setter)


def generate_field(factory, name, data):
    """Generate a well-typed field according to the data dictionary supplied
    (obtained via 'fields_get' XML-RPC/NET-RPC method).

    """
    assert 'type' in data
    field = None
    if data['type'] == 'selection':
        field = SelectionField(factory, name, data)
    elif data['type'] == 'many2many':
        field = Many2ManyField(factory, name, data)
    elif data['type'] == 'many2one':
        field = Many2OneField(factory, name, data)
    elif data['type'] == 'one2many':
        field = One2ManyField(factory, name, data)
    elif data['type'] == 'date':
        field = DateField(factory, name, data)
    elif data['type'] == 'datetime':
        field = DateTimeField(factory, name, data)
    elif data['type'] in ['char', 'float', 'integer',
                          'boolean', 'text', 'binary']:
        field = ValueField(factory, name, data)
    else:
        raise error.UnknownError(
            u"Can't instanciate the field '{field_name}', type unknown".format(
                field_name=name))
    return field

