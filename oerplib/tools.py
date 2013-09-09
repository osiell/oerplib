# -*- coding: UTF-8 -*-
##############################################################################
#
#    OERPLib
#    Copyright (C) 2013 Sébastien Alix.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""This module contains some helper functions used in ``OERPLib``."""

import re

match_version = re.compile(r'[^\d.]')


def clean_version(version):
    """Clean a version string.

        >>> from oerplib.tools import clean_version
        >>> clean_version('7.0alpha-20121206-000102')
        '7.0'

    :return: a cleaner version string
    """
    version = match_version.sub('', version.split('-')[0])
    return version


def detect_version(server, protocol, port, timeout=120):
    """Try to detect the `OpenERP` server version.

        >>> from oerplib.tools import detect_version
        >>> detect_version('localhost', 'xmlrpc', 8069)
        '7.0'

    :return: the version as string
    """
    from oerplib import rpc
    # Try to request OpenERP with the last API supported
    try:
        con = rpc.get_connector(
            server, port, protocol, timeout, version=None)
        version = con.db.server_version()
    except:
        # Try with the API of OpenERP < 6.1
        try:
            con = rpc.get_connector(
                server, port, protocol, timeout, version='6.0')
            version = con.db.server_version()
        except:
            # No version detected? Use the magic number in order to ensure the
            # use of the last API supported
            version = '42'
    finally:
        return clean_version(version)


def v(version):
    """Convert a version string in tuple. The tuple can be use to compare
    versions between them.

        >>> from oerplib.tools import v
        >>> v('7.0')
        [7, 0]
        >>> v('6.1')
        [6, 1]
        >>> v('7.0') < v('6.1')
        False

    :return: the version as tuple
    """
    return [int(x) for x in clean_version(version).split(".")]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
