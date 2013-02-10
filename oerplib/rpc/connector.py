# -*- coding: UTF-8 -*-
"""Provides connectors for different protocols."""

import abc

from oerplib.rpc import error, service
from oerplib.tools import v


class Connector(object):
    """Connector base class defining the interface used
    to interact with an OpenERP server.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, server, port, timeout, version):
        self.server = server
        try:
            int(port)
        except ValueError:
            txt = "The port '{0}' is invalid. An integer is required."
            txt = txt.format(port)
            raise error.ConnectorError(txt)
        else:
            self.port = port
        self.timeout = timeout
        self.version = version


class ConnectorXMLRPC(Connector):
    """Connector class using XMLRPC protocol."""
    def __init__(self, server, port, timeout, version):
        super(ConnectorXMLRPC, self).__init__(
            server, port, timeout, version)
        # OpenERP < 6.1
        if self.version and v(self.version) < v('6.1'):
            self._url = 'http://{server}:{port}/xmlrpc'.format(
                server=self.server, port=self.port)
        # OpenERP >= 6.1
        else:
            self._url = 'http://{server}:{port}/openerp/xmlrpc/1'.format(
                server=self.server, port=self.port)

    def __getattr__(self, service_name):
        url = self._url + '/' + service_name
        srv = service.ServiceXMLRPC(self, service_name, url)
        setattr(self, service_name, srv)
        return srv


class ConnectorXMLRPCSSL(ConnectorXMLRPC):
    """Connector class using XMLRPC protocol over SSL."""
    def __init__(self, server, port, timeout, version):
        super(ConnectorXMLRPCSSL, self).__init__(
            server, port, timeout, version)
        self._url = self._url.replace('http', 'https')


class ConnectorNetRPC(Connector):
    """Connector class using NetRPC protocol."""
    def __init__(self, server, port, timeout, version):
        super(ConnectorNetRPC, self).__init__(
            server, port, timeout, version)

    def __getattr__(self, service_name):
        srv = service.ServiceNetRPC(
            self, service_name, self.server, self.port)
        setattr(self, service_name, srv)
        return srv

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
