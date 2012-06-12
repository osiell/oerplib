# -*- coding: UTF-8 -*-
"""This module provides the BrowseRecord class."""


class BrowseRecord(object):
    """Base class that all browsable records inherit from.
    No attributes should be defined in this class (except ``_id``/``id``,
    ``__oerp__``, ``__osv__``, ``__data__`` and Python magic methods) in order
    to not be conflicted with the fields defined in the `OSV` model class on
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
                      'company_ids': [1],
                      'context_lang': 'fr_FR',
                      'context_tz': False,
                      'date': '2012-06-07 15:47:07.166421',
                      'groups_id': [2, 1, 3],
                      'id': 1,
                      'in_group_4': False,
                      'in_group_5': False,
                      'in_group_6': False,
                      'in_group_9': False,
                      'login': 'admin',
                      'menu_id': [1, 'Menu'],
                      'menu_tips': False,
                      'name': 'Administrator',
                      'new_password': '',
                      'password': 'admin',
                      'sel_groups_1_2': 2,
                      'sel_groups_3': 3,
                      'sel_groups_7_8': False,
                      'signature': 'Administrator',
                      'user_email': False,
                      'view': 'simple'}}

    In the same way, information about the `OSV` class and its columns may be
    obtained via the ``__ osv__`` attribute::

        >>> user.__osv__
        {'columns': {'action_id': <oerplib.service.osv.fields.Many2OneField object at 0xb75786ec>,
                     'active': <oerplib.service.osv.fields.ValueField object at 0xb7598b6c>,
                     'company_id': <oerplib.service.osv.fields.Many2OneField object at 0xb757868c>,
                     'company_ids': <oerplib.service.osv.fields.Many2ManyField object at 0xb75787cc>,
                     'context_lang': <oerplib.service.osv.fields.SelectionField object at 0xb7598e4c>,
                     'context_tz': <oerplib.service.osv.fields.SelectionField object at 0xb7578aec>,
                     'date': <oerplib.service.osv.fields.DateTimeField object at 0xb7585dcc>,
                     'groups_id': <oerplib.service.osv.fields.Many2ManyField object at 0xb7585bcc>,
                     'in_group_4': <oerplib.service.osv.fields.ValueField object at 0xb759abcc>,
                     'in_group_5': <oerplib.service.osv.fields.ValueField object at 0xb757870c>,
                     'in_group_6': <oerplib.service.osv.fields.ValueField object at 0xb75857ec>,
                     'in_group_9': <oerplib.service.osv.fields.ValueField object at 0xb7585b4c>,
                     'login': <oerplib.service.osv.fields.ValueField object at 0xb759a96c>,
                     'menu_id': <oerplib.service.osv.fields.Many2OneField object at 0xb7598f0c>,
                     'menu_tips': <oerplib.service.osv.fields.ValueField object at 0xb757880c>,
                     'name': <oerplib.service.osv.fields.ValueField object at 0xb759a54c>,
                     'new_password': <oerplib.service.osv.fields.ValueField object at 0xb757862c>,
                     'password': <oerplib.service.osv.fields.ValueField object at 0xb7598fec>,
                     'sel_groups_1_2': <oerplib.service.osv.fields.SelectionField object at 0xb7585dec>,
                     'sel_groups_3': <oerplib.service.osv.fields.SelectionField object at 0xb7585aac>,
                     'sel_groups_7_8': <oerplib.service.osv.fields.SelectionField object at 0xb75786cc>,
                     'signature': <oerplib.service.osv.fields.ValueField object at 0xb759a7ec>,
                     'user_email': <oerplib.service.osv.fields.ValueField object at 0xb759adac>,
                     'view': <oerplib.service.osv.fields.SelectionField object at 0xb759adec>},
         'name': 'res.users'}

    """
    __oerp__ = None
    __osv__ = None
    def __init__(self, o_id):
        self._id = o_id
        self.__data__ = {'raw_data': False, 'fields_updated': []}

    @property
    def id(self):
        """ID of the record."""
        return self._id

    def __str__(self):
        return "browse_record({osv_name}, {obj_id})".format(
                osv_name=self.__osv__['name'],
                obj_id=self._id)

    def __repr__(self):
        return str(self)

    def __getitem__(self, key):
        return getattr(self, key)

    def __eq__(self, other):
        """Compare two browse records. Return ``True`` if their ID and OSV name
        are equals.

        NOTE: the comparison is made this way because their OSV classes can be
        differents objects.

        """
        return isinstance(other, BrowseRecord) and \
            self.id == other.id and \
            self.__osv__['name'] == other.__osv__['name'] # and \
            #self.__osv__['columns'].keys() == other.__osv__['columns'].keys():

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
