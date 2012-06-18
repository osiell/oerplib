# -*- coding: UTF-8 -*-
"""This module contains classes representing the fields supported by OpenObject.
A field is a Python descriptor which defines getter/setter methods for
its related attribute.
"""
import datetime

from oerplib import error
from oerplib.service.osv import browse

def is_int(value):
    if isinstance(value, bool):
        return False
    try:
        int(value)
        return True
    except ValueError:
        return False


class BaseField(object):
    """Field which all other fields inherit.
    Manage common metadata.
    """
    def __init__(self, osv, name, data):
        self.osv = osv
        self.name = name
        self.type = 'type' in data and data['type'] or False
        self.string = 'string' in data and data['string'] or False
        self.size = 'size' in data and data['size'] or False
        self.required = 'required' in data and data['required'] or False
        self.readonly = 'readonly' in data and data['readonly'] or False
        self.help = 'help' in data and data['help'] or False
        self.states = 'states' in data and data['states'] or False

    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        pass

    def __str__(self):
        """Return a human readable string representation of the field."""
        attrs = ['string', 'relation', 'required', 'readonly', 'size', 'domain']
        attrs_rep = []
        for attr in attrs:
            if hasattr(self, attr):
                value = getattr(self, attr)
                if value:
                    if isinstance(value, basestring):
                        attrs_rep.append("{0}='{1}'".format(attr, value))
                    else:
                        attrs_rep.append("{0}={1}".format(attr, value))
        attrs_rep = ", ".join(attrs_rep)
        return "{0}({1})".format(self.type, attrs_rep)

    def check_value(self, value):
        """Check the validity of a value for the field."""
        #if self.readonly:
        #    raise error.Error(
        #        u"'{field_name}' field is readonly".format(
        #            field_name=self.name))
        if value and self.size:
            if not isinstance(value, basestring):
                raise ValueError(u"Value supplied has to be a string")
            if len(value) > self.size:
                raise ValueError(
                    u"Lenght of the '{field_name}' is limited to {size}".format(
                        field_name=self.name,
                        size=self.size))
        if not value and self.required:
            raise ValueError(
                u"'{field_name}' field require a value".format(
                    field_name=self.name))
        return value


class SelectionField(BaseField):
    """Represent the OpenObject 'fields.selection'"""
    def __init__(self, osv, name, data):
        super(SelectionField, self).__init__(osv, name, data)
        self.selection = 'selection' in data and data['selection'] or False

    def __get__(self, instance, owner):
        return getattr(instance, "_{0}".format(self.name))

    def __set__(self, instance, value):
        value = self.check_value(value)
        setattr(instance, "_{0}".format(self.name), value)
        instance.__data__['fields_updated'].append(self.name)

    def check_value(self, value):
        super(SelectionField, self).check_value(value)
        selection = [val[0] for val in self.selection]
        if value and value not in selection:
            raise ValueError(
                u"The value '{value}' supplied doesn't match with the possible "
                u"values '{selection}' for the '{field_name}' field".format(
                    value=value,
                    selection=selection,
                    field_name=self.name,
            ))
        return value


class Many2ManyField(BaseField):
    """Represent the OpenObject 'fields.many2many'"""
    def __init__(self, osv, name, data):
        super(Many2ManyField, self).__init__(osv, name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or False
        self.domain = 'domain' in data and data['domain'] or False

    def __get__(self, instance, owner):
        if getattr(instance, "_{0}".format(self.name)):
            return [instance.__oerp__.browse(self.relation, o_id)
                    for o_id in getattr(instance, "_{0}".format(self.name))]
        return []

    def __set__(self, instance, value):
        value = self.check_value(value)
        setattr(instance, "_{0}".format(self.name), value)
        instance.__data__['fields_updated'].append(self.name)

    def check_value(self, value):
        if value:
            if not isinstance(value, list):
                raise ValueError(
                        u"The value supplied has to be a list or 'False'")
        return super(Many2ManyField, self).check_value(value)


class Many2OneField(BaseField):
    """Represent the OpenObject 'fields.many2one'"""
    def __init__(self, osv, name, data):
        super(Many2OneField, self).__init__(osv, name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or False
        self.domain = 'domain' in data and data['domain'] or False

    def __get__(self, instance, owner):
        if getattr(instance, "_{0}".format(self.name)):
            return instance.__class__.__oerp__.browse(
                    self.relation,
                    getattr(instance, "_{0}".format(self.name))[0]
                )
        return False

    def __set__(self, instance, value):
        if isinstance(value, browse.BrowseRecord):
            o_rel = value
        elif is_int(value):
            o_rel = instance.__class__.__oerp__.browse(self.relation, value)
        elif value in [None, False]:
            o_rel = False
        else:
            raise ValueError(u"Value supplied has to be an integer, "
                             u"a browse_record object or False.")
        o_rel = self.check_value(o_rel)
        setattr(instance, "_{0}".format(self.name), o_rel and [o_rel.id, False])
        instance.__data__['fields_updated'].append(self.name)

    def check_value(self, value):
        super(Many2OneField, self).check_value(value)
        if value and value.__osv__['name'] != self.relation:
            raise ValueError(
                (u"Instance of '{osv_name}' supplied doesn't match with the " +\
                 u"relation '{relation}' of the '{field_name}' field.").format(
                    osv_name=value.__osv__['name'],
                    relation=self.relation,
                    field_name=self.name))
        return value


class One2ManyField(BaseField):
    """Represent the OpenObject 'fields.one2many'"""
    def __init__(self, osv, name, data):
        super(One2ManyField, self).__init__(osv, name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or False
        self.domain = 'domain' in data and data['domain'] or False

    def __get__(self, instance, owner):
        if getattr(instance, "_{0}".format(self.name)):
            return [instance.__oerp__.browse(self.relation, o_id)
                    for o_id in getattr(instance, "_{0}".format(self.name))]
        return []

    def __set__(self, instance, value):
        value = self.check_value(value)
        setattr(instance, "_{0}".format(self.name), value)
        instance.__data__['fields_updated'].append(self.name)

    def check_value(self, value):
        if value:
            if not isinstance(value, list):
                raise ValueError(
                        u"The value supplied has to be a list or 'False'")
        return super(One2ManyField, self).check_value(value)


class ReferenceField(BaseField):
    """.. versionadded:: 0.6.0
    Represent the OpenObject 'fields.reference'.
    """
    def __init__(self, osv, name, data):
        super(ReferenceField, self).__init__(osv, name, data)
        self.context = 'context' in data and data['context'] or False
        self.domain = 'domain' in data and data['domain'] or False
        self.selection = 'selection' in data and data['selection'] or False

    def __get__(self, instance, owner):
        if getattr(instance, "_{0}".format(self.name)):
            value = getattr(instance, "_{0}".format(self.name))
            relation, sep, o_id = value.rpartition(',')
            relation = relation.strip()
            o_id = int(o_id.strip())
            if relation and o_id:
                return instance.__class__.__oerp__.browse(
                        relation, o_id)
        return False

    def __set__(self, instance, value):
        value = self.check_value(value)
        setattr(instance, "_{0}".format(self.name), value)
        instance.__data__['fields_updated'].append(self.name)

    def _check_relation(self, relation):
        selection = [val[0] for val in self.selection]
        if relation not in selection:
            raise ValueError(
                (u"The value '{value}' supplied doesn't match with the possible"
                 u" values '{selection}' for the '{field_name}' field").format(
                    value=relation,
                    selection=selection,
                    field_name=self.name,
            ))
        return relation

    def check_value(self, value):
        if isinstance(value, browse.BrowseRecord):
            relation = value.__class__.__osv__['name']
            self._check_relation(relation)
            value = "%s,%s" % (relation, value.id)
            super(ReferenceField, self).check_value(value)
        elif isinstance(value, basestring):
            super(ReferenceField, self).check_value(value)
            relation, sep, o_id = value.rpartition(',')
            relation = relation.strip()
            o_id = o_id.strip()
            #o_rel = instance.__class__.__oerp__.browse(relation, o_id)
            if not relation or not is_int(o_id):
                raise ValueError(u"String not well formatted, expecting "
                                 u"'{relation},{id}' format")
            self._check_relation(relation)
        else:
            raise ValueError(u"Value supplied has to be a string or"
                             u" a browse_record object.")
        return value


class DateField(BaseField):
    """Represent the OpenObject 'fields.data'"""
    pattern = "%Y-%m-%d"
    def __init__(self, osv, name, data):
        super(DateField, self).__init__(osv, name, data)

    def __get__(self, instance, owner):
        value = getattr(instance, "_{0}".format(self.name))
        try:
            res = datetime.datetime.strptime(value, self.pattern).date()
        except Exception: # ValueError, TypeError
            res = value
        return res

    def __set__(self, instance, value):
        value = self.check_value(value)
        setattr(instance, "_{0}".format(self.name), value)
        instance.__data__['fields_updated'].append(self.name)

    def check_value(self, value):
        super(DateField, self).check_value(value)
        if isinstance(value, datetime.date):
            value = value.strftime("%Y-%m-%d")
        elif isinstance(value, basestring):
            try:
                datetime.datetime.strptime(value, self.pattern)
            except:
                raise ValueError(
                    "String not well formatted, expecting '{0}' format".format(
                        self.pattern))
        elif isinstance(value, bool):
            return value
        else:
            raise ValueError(
                    "Expecting a datetime.date object or basestring")
        return value


class DateTimeField(BaseField):
    """Represent the OpenObject 'fields.datetime'"""
    pattern = "%Y-%m-%d %H:%M:%S"
    def __init__(self, osv, name, data):
        super(DateTimeField, self).__init__(osv, name, data)

    def __get__(self, instance, owner):
        value = getattr(instance, "_{0}".format(self.name))
        try:
            res = datetime.datetime.strptime(value, self.pattern)
        except Exception: # ValueError, TypeError
            res = value
        return res

    def __set__(self, instance, value):
        value = self.check_value(value)
        setattr(instance, "_{0}".format(self.name), value)
        instance.__data__['fields_updated'].append(self.name)

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
        elif isinstance(value, bool):
            return value
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
    def __init__(self, osv, name, data):
        super(ValueField, self).__init__(osv, name, data)

    def __get__(self, instance, owner):
        return getattr(instance, "_{0}".format(self.name))

    def __set__(self, instance, value):
        value = self.check_value(value)
        setattr(instance, "_{0}".format(self.name), value)
        instance.__data__['fields_updated'].append(self.name)


def generate_field(osv, name, data):
    """Generate a well-typed field according to the data dictionary supplied
    (obtained via 'fields_get' XML-RPC/NET-RPC method).

    """
    assert 'type' in data
    field = None
    if data['type'] == 'selection':
        field = SelectionField(osv, name, data)
    elif data['type'] == 'many2many':
        field = Many2ManyField(osv, name, data)
    elif data['type'] == 'many2one':
        field = Many2OneField(osv, name, data)
    elif data['type'] == 'one2many':
        field = One2ManyField(osv, name, data)
    elif data['type'] == 'reference':
        field = ReferenceField(osv, name, data)
    elif data['type'] == 'date':
        field = DateField(osv, name, data)
    elif data['type'] == 'datetime':
        field = DateTimeField(osv, name, data)
    elif data['type'] in ['char', 'float', 'integer',
                          'boolean', 'text', 'binary']:
        field = ValueField(osv, name, data)
    else:
        txt = (u"Can't instanciate the field '{field_name}', "
               u"'{field_type}' type unknown")
        raise error.InternalError(
            txt.format(field_name=name, field_type=data['type']))
    return field

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
