# -*- coding: UTF-8 -*-
"""This module provides a `RPC` connector (via the 'get_connector' method) which
use the `XML-RPC` or `Net-RPC` protocol to communicate with an OpenERP server.
Here an example of using:

    Get a `RPC` connector object:
    >>> from oerplib import rpc
    >>> cnt = rpc.get_connector('localhost', 8070, 'netrpc')

    Login and retrieve ID of the user connected:
    >>> uid = cnt.login('database', 'user', 'passwd')

    Execute a query:
    >>> res = cnt.execute(uid, 'passwd', 'res.partner', 'read', 42)

    Execute a workflow query:
    >>> res = cnt.exec_workflow(uid, 'passwd', 'sale.order', 'order_confirm', 4)

    Download the data of a report :
    >>> data = cnt.report(uid, 'passwd', 'sale.order', 'sale.order', 4, 'pdf')

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
