# -*- coding: UTF-8 -*-
"""This module provides the BrowseRecord class."""


class BrowseRecord(object):
    """Base class that all browsable records inherit from.
    No attributes should be defined in this class (except _id/id, __oerp__,
    __osv__, __data__ and Python magic methods) in order to not be conflicted with the
    fields defined in the OSV model class on OpenERP server.

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
