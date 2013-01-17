# -*- coding: UTF-8 -*-
"""This module contains the ``Config`` class which manage the configuration
related to an instance of :class:`OERP <oerplib.OERP>`
"""

import collections


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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
