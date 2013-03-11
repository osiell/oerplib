# -*- coding: UTF-8 -*-
"""The `oerplib` module defines the :class:`OERP` class.

The :class:`OERP` class manage the client-side operations which are related to
an `OpenERP` server. You can use this one to write Python programs that performs
a variety of automated jobs that communicate with an `OpenERP` server.
"""

__author__ = 'ABF Osiell - Sebastien Alix'
__email__ = 'sebastien.alix@osiell.com'
__licence__ = 'LGPL v3'
__version__ = '0.8.0'

from oerplib.oerp import OERP
from oerplib import error
from oerplib import config


def load(name, rc_file='~/.oerplibrc'):
    """TODO"""
    data = config.get(name, rc_file)
    oerp = OERP(
        server=data['server'],
        protocol=data['protocol'],
        port=data['port'],
        timeout=data['timeout'],
    )
    oerp.login(
        user=data['user'], passwd=data['passwd'],
        database=data['database'])
    return oerp

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
