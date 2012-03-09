# -*- coding: UTF-8 -*-
"""This module provides a `RPC` connector (via the
:func:`get_connector <oerplib.rpc.get_connector>` method) which
use the `XML-RPC` or `Net-RPC` protocol to communicate with an `OpenERP` server.

Afterwards, `RPC` services (like `db`, `common` or `object`) and their methods
associated can be accessed dynamically from the connector returned.

Here is an example of how to use it:

    Get a `RPC` connector object::

    >>> from oerplib import rpc
    >>> cnt = rpc.get_connector('localhost', 8070, 'netrpc')

    Login and retrieve ID of the user connected::

    >>> uid = cnt.common.login('database', 'user', 'passwd')

    Execute a query::

    >>> res = cnt.object.execute('database', uid, 'passwd', 'res.partner', 'read', 42)

    Execute a workflow query::

    >>> res = cnt.object.exec_workflow('database', uid, 'passwd', 'sale.order', 'order_confirm', 4)

This sub-module is used by `OERPLib` to execute all queries while abstracting
the protocol used.

"""

from oerplib.rpc import connector, error

PROTOCOLS = {
        'xmlrpc': connector.ConnectorXMLRPC,
        'netrpc': connector.ConnectorNetRPC,
        }

def get_connector(server, port, protocol='xmlrpc'):
    """Return a `RPC` connector to interact with an `OpenERP` server.
    This one use either the `XML-RPC` protocol (by default) or `Net-RPC`,
    at the discretion of the user.
    """
    if protocol not in PROTOCOLS:
        txt = ("The protocol '{0}' is not supported. "
               "Please choose a protocol among these ones: {1}")
        txt = txt.format(protocol, PROTOCOLS.keys())
        raise error.ConnectorError(txt)
    return PROTOCOLS[protocol](server, port)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
