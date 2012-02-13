# -*- coding: UTF-8 -*-
"""This module contains the OSVPool class which manage OSV classes.
"""
import collections

from oerplib import osv, error


class OSVPool(collections.MutableMapping):
    """Manage OSV classes."""

    def __init__(self, oerp):
        super(OSVPool, self).__init__()
        self.oerp = oerp
        self._osv_class_by_name = {}
        self._osv_class_by_browse_class = {}

    def get_by_class(self, osv):
        """Return a OSV class which is able to create browsable objects
        corresponding to the BrowseRecord class supplied.

        """
        if osv not in self._osv_class_by_browse_class:
            raise error.InternalError(u"The class of this object is no longer"
                                      " referenced.")
        return self._osv_class_by_browse_class[osv]

    def __str__(self):
        """Return string representation of this pool."""
        #TODO: not needed when browse records will be no longer stored
        res = {}
        for osv_name, osv_class in self._osv_class_by_name.iteritems():
            res[osv_name] = osv_class.keys()
        return str(res)

    def __repr__(self):
        return str(self)

    # ---------------------------- #
    # -- MutableMapping methods -- #
    # ---------------------------- #

    def __delitem__(self, osv_name):
        browse_class = self._osv_class_by_name[osv_name].browse_class
        del self._osv_class_by_browse_class[browse_class]
        self._osv_class_by_name[osv_name].clear()
        del self._osv_class_by_name[osv_name]
        #raise error.NotAllowedError(u"Operation not supported")

    def __getitem__(self, osv_name):
        """Return an OSV class which is able to create browsable objects
        corresponding to the OSV name supplied.

        """
        if osv_name not in self._osv_class_by_name:
            osv_class = osv.OSV(self.oerp, osv_name)
            self._osv_class_by_name[osv_name] = osv_class
            self._osv_class_by_browse_class[osv_class.browse_class] =\
                    osv_class
        return self._osv_class_by_name[osv_name]

    def __iter__(self):
        for osv_name in self._osv_class_by_name:
            yield osv_name

    def __len__(self):
        return len(self._osv_class_by_name)

    def __setitem__(self, osv_name, value):
        raise error.NotAllowedError(u"Operation not supported")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
