# -*- coding: UTF-8 -*-
"""Provides the ``ConnectorXMLRPC`` and ``ConnectorNetRPC`` classes."""

#import xmlrpclib, socket
import abc
#import time

#from oerplib.rpc import error, socket_netrpc, service
from oerplib.rpc import error, service


class Connector(object):
    """Connector base class defining the interface used
    to interact with an OpenERP server.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, server, port):
        self.server = server
        try:
            int(port)
        except ValueError:
            txt = "The port '{0}' is invalid. An integer is required."
            txt = error.format(port)
            raise error.ConnectorError(txt)
        else:
            self.port = port


class ConnectorXMLRPC(Connector):
    """Connector class using XMLRPC protocol."""
    def __init__(self, server, port):
        super(ConnectorXMLRPC, self).__init__(server, port)
        self._url = 'http://{server}:{port}/xmlrpc'.format(server=self.server,
                                                           port=self.port)

    def __getattr__(self, service_name):
        url = self._url + '/' + service_name
        srv = service.ServiceXMLRPC(service_name, url)
        setattr(self, service_name, srv)
        return srv


class ConnectorNetRPC(Connector):
    """Connector class using NetRPC protocol."""
    def __init__(self, server, port):
        super(ConnectorNetRPC, self).__init__(server, port)

    def __getattr__(self, service_name):
        srv = service.ServiceNetRPC(service_name, self.server, self.port)
        setattr(self, service_name, srv)
        return srv

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
