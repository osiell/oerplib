# -*- coding: UTF-8 -*-
##############################################################################
#
#    OERPLib
#    Copyright (C) 2011-2013 Sébastien Alix.
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

    >>> cnt.proxy.web.session.authenticate(db='database', login='admin', password='admin')
    {u'jsonrpc': u'2.0', u'id': 202516757,
     u'result': {u'username': u'admin', u'user_context': {u'lang': u'fr_FR', u'tz': u'Europe/Brussels', u'uid': 1},
     u'db': u'test70', u'uid': 1, u'session_id': u'308816f081394a9c803613895b988540'}}

    Read data of a partner:

    >>> cnt.proxy.web.dataset.call(model='res.partner', method='read', args=[[42]])
    {u'jsonrpc': u'2.0', u'id': 454236230,
     u'result': [{u'id': 42, u'comment': False, u'ean13': False, u'property_account_position': False, ...}]}

    You can send requests this way too:

    >>> cnt.proxy['/web/dataset'].call(model='res.partner', method='read', args=[[42]])
    {u'jsonrpc': u'2.0', u'id': 328686288,
     u'result': [{u'id': 42, u'comment': False, u'ean13': False, u'property_account_position': False, ...}]}

    Or like this:

    >>> cnt.proxy['web']['dataset'].call(model='res.partner', method='read', args=[[42]])
    {u'jsonrpc': u'2.0', u'id': 102320639,
     u'result': [{u'id': 42, u'comment': False, u'ean13': False, u'property_account_position': False, ...}]}

"""
from oerplib.rpc import error, service, jsonrpclib
from oerplib.tools import v

# XML-RPC available paths for OpenERP
# '/xmlrpc'             => 5.0, 6.0, 8.0
# '/openerp/xmlrpc/1'   => 6.1, 7.0
# '/xmlrpc/2'           => 8.0
XML_RPC_PATHS = ['/xmlrpc', '/openerp/xmlrpc/1', '/xmlrpc/2']


class Connector(object):
    """Connector base class defining the interface used
    to interact with an `OpenERP` server.
    """
    def __init__(self, server, port=8069, timeout=120, version=None):
        self.server = server
        try:
            int(port)
        except ValueError:
            txt = "The port '{0}' is invalid. An integer is required."
            txt = txt.format(port)
            raise error.ConnectorError(txt)
        else:
            self.port = int(port)
        self._timeout = timeout
        self.version = version
        self._url = None

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout


class ConnectorXMLRPC(Connector):
    """Connector class using the `XML-RPC` protocol."""
    def __init__(self, server, port=8069, timeout=120, version=None):
        super(ConnectorXMLRPC, self).__init__(
            server, port, timeout, version)
        if self.version:
            # OpenERP < 6.1
            if v(self.version) < v('6.1'):
                self._url = 'http://{server}:{port}/xmlrpc'.format(
                    server=self.server, port=self.port)
            # OpenERP >= 6.1 and < 8.0
            elif v(self.version) < v('8.0'):
                self._url = 'http://{server}:{port}/openerp/xmlrpc/1'.format(
                    server=self.server, port=self.port)
            # OpenERP >= 8.0
            elif v(self.version) >= v('8.0'):
                self._url = 'http://{server}:{port}/xmlrpc/2'.format(
                    server=self.server, port=self.port)
        # Detect the XML-RPC path to use
        if self._url is None:
            # We begin with the last known XML-RPC path to give the priority to
            # the last version of OpenERP supported
            paths = XML_RPC_PATHS[:]
            paths.reverse()
            for path in paths:
                url = 'http://{server}:{port}{path}'.format(
                    server=self.server, port=self.port, path=path)
                try:
                    db = service.ServiceXMLRPC(
                        self, 'db', '{url}/{srv}'.format(url=url, srv='db'))
                    version = db.server_version()
                except error.ConnectorError:
                    continue
                else:
                    self._url = url
                    self.version = version
                    break

    def __getattr__(self, service_name):
        url = self._url + '/' + service_name
        srv = service.ServiceXMLRPC(self, service_name, url)
        setattr(self, service_name, srv)
        return srv


class ConnectorXMLRPCSSL(ConnectorXMLRPC):
    """Connector class using the `XML-RPC` protocol over SSL."""
    def __init__(self, server, port=8069, timeout=120, version=None):
        super(ConnectorXMLRPCSSL, self).__init__(
            server, port, timeout, version)
        self._url = self._url.replace('http', 'https')


class ConnectorNetRPC(Connector):
    """Connector class using the `Net-RPC` protocol."""
    def __init__(self, server, port=8070, timeout=120, version=None):
        super(ConnectorNetRPC, self).__init__(
            server, port, timeout, version)

    def __getattr__(self, service_name):
        srv = service.ServiceNetRPC(
            self, service_name, self.server, self.port)
        setattr(self, service_name, srv)
        return srv


class ConnectorJSONRPC(Connector):
    """Connector class using the `JSON-RPC` protocol."""
    def __init__(self, server, port=8069, timeout=120, version=None,
                 deserialize=True):
        self.proxy = jsonrpclib.AuthProxy(
            server, port, timeout, ssl=False, deserialize=deserialize)
        super(ConnectorJSONRPC, self).__init__(
            server, port, timeout, version)

    @property
    def timeout(self):
        return self.proxy._timeout

    @timeout.setter
    def timeout(self, timeout):
        self.proxy._timeout = timeout


class ConnectorJSONRPCSSL(ConnectorJSONRPC):
    """Connector class using the `JSON-RPC` protocol over `SSL`."""
    def __init__(self, server, port=8069, timeout=120, version=None,
                 deserialize=True):
        self.proxy = jsonrpclib.AuthProxy(
            server, port, timeout, ssl=True, deserialize=deserialize)
        super(ConnectorJSONRPCSSL, self).__init__(
            server, port, timeout, version)


PROTOCOLS = {
    'xmlrpc': ConnectorXMLRPC,
    'xmlrpc+ssl': ConnectorXMLRPCSSL,
    'jsonrpc': ConnectorJSONRPC,
    'jsonrpc+ssl': ConnectorJSONRPCSSL,
    'netrpc': ConnectorNetRPC,
}


def get_connector(server, port=8069, protocol='xmlrpc',
                  timeout=120, version=None):
    """Return a `RPC` connector to interact with an `OpenERP` server.
    Supported protocols are:

        - ``xmlrpc``: Standard `XML-RPC` protocol (default),
        - ``xmlrpc+ssl``: `XML-RPC` protocol over `SSL`,
        - ``netrpc``: `Net-RPC` protocol made by `OpenERP` (no longer available
          since `OpenERP v7.0`).
        - ``jsonrpc``: `JSON-RPC` protocol,
        - ``jsonrpc+ssl``: `JSON-RPC` protocol over `SSL`,

    If the `version` parameter is set to `None`, the last API supported will
    be used to send requests to `OpenERP`. Otherwise, you can force the
    API to use with the corresponding string version
    (e.g.: ``'6.0', '6.1', '7.0', ...``):

        >>> from oerplib import rpc
        >>> cnt = rpc.get_connector('localhost', 8069, 'xmlrpc', version='7.0')
    """
    if protocol not in PROTOCOLS:
        txt = ("The protocol '{0}' is not supported. "
               "Please choose a protocol among these ones: {1}")
        txt = txt.format(protocol, PROTOCOLS.keys())
        raise error.ConnectorError(txt)
    return PROTOCOLS[protocol](server, port, timeout, version)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
