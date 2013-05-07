# -*- coding: UTF-8 -*-
"""This module contains the ``Config`` class which manage the configuration
related to an instance of :class:`OERP <oerplib.OERP>`, and others useful
functions used internally.
"""

import collections
import os
import stat
from ConfigParser import SafeConfigParser

from oerplib import error


class Config(collections.MutableMapping):
    """Class which manage the configuration of an
    :class:`OERP <oerplib.OERP>` instance.
    """
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


def get_all(rc_file='~/.oerplibrc'):
    """Return session configurations from the `rc_file` file."""
    conf = SafeConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    sessions = {}
    for name in conf.sections():
        sessions[name] = {
            'server': conf.get(name, 'server'),
            'protocol': conf.get(name, 'protocol'),
            'port': conf.getint(name, 'port'),
            'timeout': conf.getint(name, 'timeout'),
            'user': conf.get(name, 'user'),
            'passwd': conf.get(name, 'passwd'),
            'database': conf.get(name, 'database'),
        }
    return sessions


def get(name, rc_file='~/.oerplibrc'):
    """Return the session configuration identified by `name`
    from the `rc_file` file.

    :raise: :class:`oerplib.error.Error`
    """
    conf = SafeConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        raise error.Error(
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


def list(rc_file='~/.oerplibrc'):
    """Return a list of all configurations available in the
    `rc_file` file.
    """
    conf = SafeConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    return conf.sections()


def save(name, data, rc_file='~/.oerplibrc'):
    """Save the `data` session configuration under the name `name`.
    in the `rc_file` file.
    """
    conf = SafeConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        conf.add_section(name)
    for k, v in data.iteritems():
        conf.set(name, k, str(v))
    with open(os.path.expanduser(rc_file), 'wb') as file_:
        os.chmod(os.path.expanduser(rc_file), stat.S_IREAD | stat.S_IWRITE)
        conf.write(file_)


def remove(name, rc_file='~/.oerplibrc'):
    """Remove the session configuration identified by `name`
    from the `rc_file` file.

    :raise: :class:`oerplib.error.Error`
    """
    conf = SafeConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    res = conf.remove_section(name)
    with open(os.path.expanduser(rc_file), 'wb') as file_:
        conf.write(file_)
    return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
