# -*- coding: UTF-8 -*-

import xmlrpclib
import httplib
import socket
import sys


class TimeoutServerProxy(xmlrpclib.ServerProxy):
    """xmlrpclib.ServerProxy overload to manage the timeout of the socket."""
    def __init__(self, *args, **kwargs):
        t = TimeoutTransport()
        t.timeout = kwargs.get('timeout', 120)
        if 'timeout' in kwargs:
            del kwargs['timeout']
        kwargs['transport'] = t
        xmlrpclib.ServerProxy.__init__(self, *args, **kwargs)


# Python 2.5 and 2.6
class TimeoutHTTPPy26(httplib.HTTP):
   def __init__(self, host='', port=None, strict=None,
                timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        if port == 0:
            port = None
        self._setup(self._connection_class(host, port, strict, timeout))

class TimeoutTransportPy26(xmlrpclib.Transport):
    def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, *args, **kwargs):
        xmlrpclib.Transport.__init__(self, *args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        host, extra_headers, x509 = self.get_host_info(host)
        conn = TimeoutHTTPPy26(host, timeout=self.timeout)
        return conn


# Python 2.7
class TimeoutHTTPConnectionPy27(httplib.HTTPConnection):
    def __init__(self, timeout, *args, **kwargs):
        httplib.HTTPConnection.__init__(self, *args, **kwargs)
        self.timeout = timeout

    def connect(self):
        httplib.HTTPConnection.connect(self)
        self.sock.settimeout(self.timeout)

class TimeoutTransportPy27(xmlrpclib.Transport):
    def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, *args, **kwargs):
        xmlrpclib.Transport.__init__(self, *args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        if self._connection and host == self._connection[0]:
            return self._connection[1]

        chost, self._extra_headers, x509 = self.get_host_info(host)
        self._connection = host, TimeoutHTTPConnectionPy27(self.timeout, chost)
        return self._connection[1]


# Define the TimeTransport class version to use
TimeoutTransport = sys.version_info <= (2, 7) \
        and TimeoutTransportPy26 \
        or TimeoutTransportPy27

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
