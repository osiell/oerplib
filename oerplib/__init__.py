# -*- coding: UTF-8 -*-
"""This module defines the :class:`OERP` and :class:`DMS` classes.

The :class:`OERP` class manage the client-side operations which are related to an OpenERP
server. You can use this to write Python programs that performs a variety of
automated jobs that communicate with an OpenERP server.

"""
"""
The :class:`DMS` class manage the Document Management System of an OpenERP server. This one
inherits from `ftplib.FTP <http://docs.python.org/library/ftplib.html>`_ class and has few methods to facilitate some tasks.

"""
from oerplib.oerp import OERP
from oerplib.dms import DMS
from oerplib import error

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
