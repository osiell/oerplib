# -*- coding: UTF-8 -*-
"""This module provides `RPC` connectors (via the
:func:`get_connector <oerplib.rpc.get_connector>` function) which use the
`XML-RPC`, `Net-RPC` or `JSON-RPC` protocol to communicate with an
`OpenERP` server.

Afterwards, `RPC` services and their associated methods can be accessed
dynamically from the connector returned.

`XML-RPC` and `Net-RPC` provide the same interface, such as services like
``db``, ``common`` or ``object``.
On the other hand, `JSON-RPC` provides a completely different interface, with
services provided by Web modules of `OpenERP` like ``web/session``,
``web/dataset`` and so on.

Here is an example of how to use the first:

    Get a `RPC` connector object::

    >>> from oerplib import rpc
    >>> cnt = rpc.get_connector('localhost', 8069, 'xmlrpc')

    Login and retrieve ID of the user connected::

    >>> uid = cnt.common.login('database', 'user', 'passwd')

    Execute a query::

    >>> res = cnt.object.execute('database', uid, 'passwd', 'res.partner', 'read', [42])

    Execute a workflow query::

    >>> res = cnt.object.exec_workflow('database', uid, 'passwd', 'sale.order', 'order_confirm', 4)

And here the `JSON-RPC` way:

    >>> from oerplib import rpc
    >>> cnt = rpc.get_connector('localhost', 8069, 'jsonrpc')

    Open a user session:

    >>> cnt.web.session.authenticate(db='database', login='admin', password='admin')
    {u'jsonrpc': u'2.0', u'id': 202516757,
     u'result': {u'username': u'admin', u'user_context': {u'lang': u'fr_FR', u'tz': u'Europe/Brussels', u'uid': 1},
     u'db': u'test70', u'uid': 1, u'session_id': u'308816f081394a9c803613895b988540'}}

    Read data of a partner:

    >>> cnt.web.dataset.call(model='res.partner', method='read', args=[[42]])
    {u'jsonrpc': u'2.0', u'id': 454236230,
     u'result': [{u'id': 42, u'comment': False, u'ean13': False, u'property_account_position': False, ...}]}


This sub-module is used by `OERPLib` to execute all queries while abstracting
the protocol used.

"""

from oerplib.rpc import connector, error

PROTOCOLS = {
    'xmlrpc': connector.ConnectorXMLRPC,
    'xmlrpc+ssl': connector.ConnectorXMLRPCSSL,
    'jsonrpc': connector.ConnectorJSONRPC,
    'jsonrpc+ssl': connector.ConnectorJSONRPCSSL,
    'netrpc': connector.ConnectorNetRPC,
}


def get_connector(server, port=8069, protocol='xmlrpc',
                  timeout=120, version=None):
    """Return a `RPC` connector to interact with an `OpenERP` server.
    Supported protocols are:

        - ``xmlrpc``: Standard `XML-RPC` protocol (default),
        - ``xmlrpc+ssl``: `XML-RPC` protocol over `SSL`,
        - ``jsonrpc``: `JSON-RPC` protocol,
        - ``jsonrpc+ssl``: `JSON-RPC` protocol over `SSL`,
        - ``netrpc``: `Net-RPC` protocol made by `OpenERP` (no longer available
          since `OpenERP v7.0`).

    If the `version` parameter is set to `None`, the last API supported will
    be used to send requests to `OpenERP`. Otherwise, you can force the
    API to use with the corresponding string version
    (e.g.: ``'6.0', '6.1', '7.0', ...``):

        >>> from oerplib import rpc
        >>> cnt = rpc.get_connector('localhost', 8069, 'xmlrpc', version='6.1')
    """
    if protocol not in PROTOCOLS:
        txt = ("The protocol '{0}' is not supported. "
               "Please choose a protocol among these ones: {1}")
        txt = txt.format(protocol, PROTOCOLS.keys())
        raise error.ConnectorError(txt)
    return PROTOCOLS[protocol](server, port, timeout, version)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
