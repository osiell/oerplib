# -*- coding: UTF-8 -*-
"""This module provides the OSV class"""


class OSV(object):
    """Base class that all OSV classes inherit from.
    No attributes should be defined in this class (except _id/id, __oerp__,
    __osv__ and Python magic methods) in order to not be conflicted with the
    fields defined in the OSV-base class on OpenERP server.

    """
    __slots__ = ['__oerp__']
    def __init__(self, o_id):
        self._id = o_id
        self.__osv__ = None

    @property
    def id(self):
        return self._id

    def __str__(self):
        return "browse_record({osv_name}, {obj_id})".format(
                osv_name=self.__osv__['name'],
                obj_id=self._id)

    def __repr__(self):
        return str(self)
