# -*- coding: UTF-8 -*-
"""This module contains some helper functions used in ``OERPLib``."""

import re


def convert_version(version):
    version = version.split('-')[0]
    return version


def detect_version(server, protocol, port, timeout):
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
        return convert_version(version)


def v(version):
    return [int(x) for x in re.sub(r'(\.0+)*$', '', version).split(".")]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
