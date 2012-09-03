# -*- coding: UTF-8 -*-

import xmlrpclib

from oerplib.rpc import socket_netrpc, xmlrpclib_custom, error


class ServiceXMLRPC(object):
    def __init__(self, connector, name, url):
        self._connector = connector
        self._name = name
        self._url = url

    def __getattr__(self, method):
        def rpc_method(*args):
            try:
                self._sock = xmlrpclib_custom.TimeoutServerProxy(
                        self._url, allow_none=True,
                        timeout=self._connector.timeout)
                sock_method = getattr(self._sock, method, False)
                return sock_method(*args)
            #NOTE: exception raised with these kind of requests:
            #   - execute('fake.model', 'search', [])
            #   - execute('sale.order', 'fake_method')
            except xmlrpclib.Fault as exc:
                # faultCode: error message
                # faultString: OpenERP server traceback (following the OpenERP
                # server version used, a bad request can produce a
                # server traceback, or not).
                raise error.ConnectorError(exc.faultCode, exc.faultString)
            #TODO NEED TEST (when is raised this exception?)
            except xmlrpclib.Error as exc:
                raise error.ConnectorError(' - '.join(exc.args))
        return rpc_method


class ServiceNetRPC(object):
    def __init__(self, connector, name, server, port):
        self._connector = connector
        self._name = name
        self._server = server
        self._port = port

    def __getattr__(self, method):
        def rpc_method(*args):
            try:
                sock = socket_netrpc.NetRPC(timeout=self._connector.timeout)
                sock.connect(self._server, self._port)
                sock.send((self._name, method, )+args)
                result = sock.receive()
                sock.disconnect()
                return result
            #NOTE: exception raised with these kind of requests:
            #   - execute('fake.model', 'search', [])
            #   - execute('sale.order', 'fake_method')
            except socket_netrpc.NetRPCError as exc:
                # faultCode: error message
                # faultString: OpenERP server traceback (following the OpenERP
                # server version used, a bad request can produce a
                # server traceback, or not).
                raise error.ConnectorError(exc.faultCode, exc.faultString)
        return rpc_method

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
