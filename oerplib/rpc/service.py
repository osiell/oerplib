# -*- coding: UTF-8 -*-

import xmlrpclib
import socket

from oerplib.rpc import socket_netrpc, error


class ServiceXMLRPC(object):
    def __init__(self, name, url):
        self._name = name
        self._url = url
        self._sock = xmlrpclib.ServerProxy(self._url, allow_none=True)

    def __getattr__(self, method):
        def rpc_method(*args):
            try:
                sock_method = getattr(self._sock, method, False)
                return sock_method(*args)
            #TODO NEED TEST
            except xmlrpclib.Fault as exc:
                raise error.ConnectorError(
                        repr(exc.faultCode) + ': ' + exc.faultString)
            #TODO NEED TEST
            except xmlrpclib.Error as exc:
                raise error.ConnectorError(' - '.join(exc.args))
            except socket.error as exc:
                raise error.ConnectorError(exc.strerror)
        return rpc_method


class ServiceNetRPC(object):
    def __init__(self, name, server, port):
        self._name = name
        self._server = server
        self._port = port

    def __getattr__(self, method):
        def rpc_method(*args):
            try:
                sock = socket_netrpc.NetRPC()
                sock.connect(self._server, self._port)
                sock.send((self._name, method, )+args)
                result = sock.receive()
                sock.disconnect()
                return result
            #TODO NEED TEST
            except socket_netrpc.NetRPCError as exc:
                raise error.ConnectorError(unicode(exc))
            except socket.error as exc:
                raise error.ConnectorError(exc.strerror)
        return rpc_method

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
