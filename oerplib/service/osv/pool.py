# -*- coding: UTF-8 -*-
"""This module contains the Pool class which manage OSV classes."""

from oerplib.service.osv import osv


class Pool(object):
    """Manage OSV classes."""

    def __init__(self, oerp):
        super(Pool, self).__init__()
        self.oerp = oerp

    def get(self, osv_name):
        """Return an OSV class which is able to create browsable records
        corresponding to the OSV name supplied.

        """
        return osv.OSV(self.oerp, osv_name)

    def get_by_class(self, browse_class):
        """Return a OSV class which is able to create browsable records
        corresponding to the BrowseRecord class supplied.

        """
        return osv.OSV(self.oerp, browse_class.__osv__['name'])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
