# -*- coding: UTF-8 -*-

import xmlrpclib
import httplib
import socket
import sys
from urlparse import urlparse

TimeoutTransport = None  # Defined later
TimeoutSafeTransport = None  # Defined later


class TimeoutServerProxy(xmlrpclib.ServerProxy):
    """xmlrpclib.ServerProxy overload to manage the timeout of the socket."""
    def __init__(self, *args, **kwargs):
        url = args[0]
        https_ok = urlparse(url).scheme == 'https'
        t = https_ok and TimeoutSafeTransport() or TimeoutTransport()
        t.timeout = kwargs.get('timeout', 120)
        if 'timeout' in kwargs:
            del kwargs['timeout']
        kwargs['transport'] = t
        xmlrpclib.ServerProxy.__init__(self, *args, **kwargs)


if sys.version_info <= (2, 7):
    # Python 2.5 and 2.6
    class TimeoutHTTPPy26(httplib.HTTP):
        def __init__(self, host='', port=None, strict=None,
                     timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
            if port == 0:
                port = None
            self._setup(self._connection_class(host, port, strict, timeout))

    class TimeoutTransportPy26(xmlrpclib.Transport):
        def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                     *args, **kwargs):
            xmlrpclib.Transport.__init__(self, *args, **kwargs)
            self.timeout = timeout

        def make_connection(self, host):
            host, extra_headers, x509 = self.get_host_info(host)
            conn = TimeoutHTTPPy26(host, timeout=self.timeout)
            return conn

    # Define the TimeTransport class version to use
    TimeoutTransport = TimeoutTransportPy26
    TimeoutSafeTransport = TimeoutTransportPy26  # TODO
else:
    # Python 2.7 and 3.X

    # -- xmlrpclib.Transport with timeout support --

    class TimeoutHTTPConnectionPy27(httplib.HTTPConnection):
        def __init__(self, timeout, *args, **kwargs):
            httplib.HTTPConnection.__init__(self, *args, **kwargs)
            self.timeout = timeout

        def connect(self):
            httplib.HTTPConnection.connect(self)
            self.sock.settimeout(self.timeout)

    class TimeoutTransportPy27(xmlrpclib.Transport):
        def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                     *args, **kwargs):
            xmlrpclib.Transport.__init__(self, *args, **kwargs)
            self.timeout = timeout

        def make_connection(self, host):
            if self._connection and host == self._connection[0]:
                return self._connection[1]

            chost, self._extra_headers, x509 = self.get_host_info(host)
            self._connection = host, TimeoutHTTPConnectionPy27(
                self.timeout, chost)
            return self._connection[1]

    # -- xmlrpclib.SafeTransport with timeout support --

    class TimeoutHTTPSConnectionPy27(httplib.HTTPSConnection):
        def __init__(self, timeout, *args, **kwargs):
            httplib.HTTPSConnection.__init__(self, *args, **kwargs)
            self.timeout = timeout

        def connect(self):
            httplib.HTTPSConnection.connect(self)
            self.sock.settimeout(self.timeout)

    class TimeoutSafeTransportPy27(xmlrpclib.SafeTransport):
        def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                     *args, **kwargs):
            xmlrpclib.SafeTransport.__init__(self, *args, **kwargs)
            self.timeout = timeout

        def make_connection(self, host):
            if self._connection and host == self._connection[0]:
                return self._connection[1]

            chost, self._extra_headers, x509 = self.get_host_info(host)
            self._connection = host, TimeoutHTTPSConnectionPy27(
                self.timeout, chost)
            return self._connection[1]

    # Define the TimeTransport class version to use
    TimeoutTransport = TimeoutTransportPy27
    TimeoutSafeTransport = TimeoutSafeTransportPy27

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
