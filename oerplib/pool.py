# -*- coding: UTF-8 -*-
"""This module contains the OSVPool class which manage OSV classes."""

from oerplib import osv


class OSVPool(object):
    """Manage OSV classes."""

    def __init__(self, oerp):
        super(OSVPool, self).__init__()
        self.oerp = oerp

    def get(self, osv_name):
        """Return an OSV class which is able to create browsable objects
        corresponding to the OSV name supplied.

        """
        return osv.OSV(self.oerp, osv_name)

    def get_by_class(self, browse_class):
        """Return a OSV class which is able to create browsable objects
        corresponding to the BrowseRecord class supplied.

        """
        #if browse_class not in self._osv_class_by_browse_class:
        #    raise error.InternalError(u"The class of this object is no longer"
        #                              " referenced.")
        #return self._osv_class_by_browse_class[browse_class]
        return osv.OSV(self.oerp, browse_class.__osv__['name'])

    #def __str__(self):
    #    """Return string representation of this pool."""
    #    #TODO: not needed when browse records will be no longer stored
    #    res = {}
    #    for osv_name, osv_class in self._osv_class_by_name.iteritems():
    #        res[osv_name] = osv_class.keys()
    #    return str(res)

    #def __repr__(self):
    #    return str(self)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
