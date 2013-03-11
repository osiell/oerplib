# -*- coding: UTF-8 -*-
"""This module contains the ``Config`` class which manage the configuration
related to an instance of :class:`OERP <oerplib.OERP>`
"""

import collections
import os
from ConfigParser import SafeConfigParser

from oerplib import error


class Config(collections.MutableMapping):
    """"""
    def __init__(self, oerp, options):
        super(Config, self).__init__()
        self._oerp = oerp
        self._options = options or {}

    def __getitem__(self, key):
        return self._options[key]

    def __setitem__(self, key, value):
        """Handle ``timeout`` option to set the timeout on the connector."""
        if key == 'timeout':
            self._oerp._connector.timeout = value
        self._options[key] = value

    def __delitem__(self, key):
        # TODO raise exception
        pass

    def __iter__(self):
        return self._options.__iter__()

    def __len__(self):
        return len(self._options)

    def __str__(self):
        return self._options.__str__()

    def __repr__(self):
        return self._options.__repr__()


def get(name, rc_file='~/.oerplibrc'):
    """TODO"""
    conf = SafeConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        raise error.InternalError(
            "'{0}' configuration does not exist".format(name))
    return {
        'server': conf.get(name, 'server'),
        'protocol': conf.get(name, 'protocol'),
        'port': conf.getint(name, 'port'),
        'timeout': conf.getint(name, 'timeout'),
        'user': conf.get(name, 'user'),
        'passwd': conf.get(name, 'passwd'),
        'database': conf.get(name, 'database'),
    }


def save(name, data, rc_file='~/.oerplibrc'):
    """TODO"""
    conf = SafeConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        conf.add_section(name)
    for k, v in data.iteritems():
        conf.set(name, k, str(v))
    with open(os.path.expanduser(rc_file), 'wb') as file_:
        os.chmod(os.path.expanduser(rc_file), 0600)
        conf.write(file_)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
