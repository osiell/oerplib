# -*- coding: UTF-8 -*-
"""This module provides the BrowseRecord class."""


class BrowseRecord(object):
    """Base class that all browsable records inherit from.
    No attributes should be defined in this class (except ``_id``/``id``,
    ``__oerp__``, ``__osv__``, ``__data__`` and Python magic methods) in order
    to not be conflicted with the fields defined in the model class on
    the `OpenERP` server.

    A reference to the :class:`OERP <oerplib.OERP>` object used to instanciate
    a ``browse_record`` is available through the ``__oerp__`` attribute::

        >>> oerp = oerplib.OERP('localhost')
        >>> user = oerp.login('admin', 'admin', 'db_name')
        >>> user.__oerp__ == oerp
        True

    The ``__data__`` attribute is used to store some data related to the
    record (it is not recommended to edit them)::

        >>> user.__data__
        {'fields_updated': [],
         'raw_data': {'action_id': False,
                      'active': True,
                      'company_id': [1, 'Your Company'],
                      ...},
         'values': {'action_id': False,
                    'active': True,
                    'company_id': [1, 'Your Company'],
                    ...}}

    In the same way, information about the model class and its columns may be
    obtained via the ``__osv__`` attribute::

        >>> user.__osv__
        {'columns': {'action_id': <oerplib.service.osv.fields.Many2OneField object at 0xb75786ec>,
                     'active': <oerplib.service.osv.fields.ValueField object at 0xb7598b6c>,
                     'company_id': <oerplib.service.osv.fields.Many2OneField object at 0xb757868c>,
                     ...},
         'name': 'res.users'}

    """
    __oerp__ = None
    __osv__ = None

    def __init__(self, o_id):
        self._id = o_id
        self.__data__ = {'values': {}, 'raw_data': {}, 'fields_updated': []}

    @property
    def id(self):
        """ID of the record."""
        return self._id

    def __repr__(self):
        return "browse_record(%r, %r)" % (self.__osv__['name'], self._id)

    def __getitem__(self, key):
        return getattr(self, key)

    def __int__(self):
        return self._id

    def __eq__(self, other):
        """Compare two browse records. Return ``True`` if their ID and model
        name are equals.

        NOTE: the comparison is made this way because their model classes can be
        differents objects.

        """
        return isinstance(other, BrowseRecord) and \
            self.id == other.id and \
            self.__osv__['name'] == other.__osv__['name']

    def __ne__(self, other):
        if not isinstance(other, BrowseRecord):
            return True
        return isinstance(other, BrowseRecord)\
            and (self.__osv__['name'], self.id) !=\
                (other.__osv__['name'], other.id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
