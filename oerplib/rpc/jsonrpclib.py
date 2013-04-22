# -*- coding: utf-8 -*-
"""Provides the :class:`Proxy` and :class:`AuthProxy` classes."""
import urllib2
import cookielib
import json
import random


class Proxy(object):
    """The :class:`Proxy` class provides a dynamic access
    to all JSON methods.
    """
    def __init__(self, host, port, timeout=120, ssl=False):
        self._root_url = "{http}{host}:{port}".format(
            http=(ssl and "https://" or "http://"), host=host, port=port)
        self._timeout = timeout
        self._builder = URLBuilder(self)
        cookie_jar = cookielib.CookieJar()
        self._opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cookie_jar))

    def __getattr__(self, name):
        return getattr(self._builder, name)

    def __call__(self, url, params):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "call",
            "params": params,
            "id": random.randint(0, 1000000000),
        })
        request = urllib2.Request(url='/'.join([self._root_url, url]))
        request.add_header('Content-Type', 'application/json')
        request.add_data(data)
        response = self._opener.open(request, timeout=self._timeout)
        result = json.load(response)
        return result


class AuthProxy(Proxy):
    """In addition to :class:`Proxy`, the :class:`AuthProxy` class
    simplifies request handling by adding automatically the ``session_id``
    parameter once the user is authenticated.
    """
    def __init__(self, host, port, timeout=120, ssl=False):
        super(AuthProxy, self).__init__(host, port, timeout, ssl)
        self._session_id = None

    def __call__(self, url, params):
        # Add the 'session_id' parameter if necessary
        if url == 'web/session/authenticate':
            result = super(AuthProxy, self).__call__(url, params)
            self._session_id = result and result['result']['session_id']
            return result
        elif self._session_id and 'session_id' not in params:
            params['session_id'] = self._session_id
        return super(AuthProxy, self).__call__(url, params)


class URLBuilder(object):
    """Auto-builds an URL while getting its attributes.
    Used by :class:`Proxy` and :class:`Proxy` classes.
    """
    def __init__(self, rpc, url=None):
        self._rpc = rpc
        self._url = url

    def __getattr__(self, path):
        new_url = self._url and '/'.join([self._url, path]) or path
        return URLBuilder(self._rpc, new_url)

    def __call__(self, **kwargs):
        return self._rpc(self._url, kwargs)

    def __str__(self):
        return self._url
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
