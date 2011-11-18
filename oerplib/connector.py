# -*- coding: UTF-8 -*-
"""This module provides a connector (via the 'get_connector' method)
which use the XMLRPC or NetRPC protocol. Ex:

Get a connector object:
    >>> import connector
    >>> cnt = connector.get_connector('localhost', 8070, 'netrpc')

Login and retrieve ID of the user connected:
    >>> uid = cnt.login('user', 'passwd', 'database')

Execute a query:
    >>> res = cnt.execute('database', uid, 'passwd', 'res.partner', 'read', 42)
"""

import xmlrpclib, socket
import abc
import time

def get_connector(server, port, protocol='xmlrpc'):
    """Return a Connector class to interact with an OpenERP server.
    This one use either the XMLRPC protocol (by default) or NetRPC,
    at the discretion of the user.
    """
    connector = {
            'xmlrpc': _ConnectorXMLRPC,
            'netrpc': _ConnectorNetRPC,
            }[protocol](server, port)
    return connector


class _Connector(object):
    """Connector base class defining the interface used
    to interact with an OpenERP server.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, server, port):
        self.server = server
        self.port = port

    @abc.abstractmethod
    def login(self, user, passwd, database):
        """Log in the user on a database. Return the user's ID."""
        pass

    @abc.abstractmethod
    def execute(self, database, uid, upasswd, osv_name, method, *args):
        """Execute a simple RPC query."""
        pass

    @abc.abstractmethod
    def exec_workflow(self, *args):
        """Execute a RPC workflow query."""
        pass

    @abc.abstractmethod
    def exec_report(self, database, uid, passwd, report_id):
        """Execute a RPC query to retrieve a report."""
        pass


class _ConnectorXMLRPC(_Connector):
    """Connector class using XMLRPC protocol."""
    def __init__(self, server, port):
        super(_ConnectorXMLRPC, self).__init__(server, port)
        self.url = 'http://{server}:{port}/xmlrpc'.format(server=self.server,
                                                          port=self.port)
        self.sock = xmlrpclib.ServerProxy(self.url+'/object')
        self.sock_report = xmlrpclib.ServerProxy(self.url+'/report')
        self.sock_common = xmlrpclib.ServerProxy(self.url+'/common')

    def login(self, user, passwd, database):
        try:
            user_id = self.sock_common.login(database, user, passwd)
        except xmlrpclib.Fault as exc:
            #NOTE: exc.faultCode is in unicode and Exception doesn't
            # handle unicode object
            raise Exception(repr(exc.faultCode))
        except socket.error as exc:
            raise Exception(exc.strerror)
        else:
            return user_id

    def execute(self, database, uid, upasswd, osv_name, method, *args):
        try:
            return self.sock.execute(database, uid, upasswd,
                                     osv_name, method, *args)
        #FIXME: review exceptions management
        except xmlrpclib.Error as exc:
            raise Exception("{0}: {1}".format(exc.faultCode or "Unknown error",
                                               exc.faultString))

    def exec_workflow(self, database, uid, upasswd, *args):
        #TODO need to be tested + fix exception
        try:
            return self.sock.exec_workflow(database, uid, upasswd, *args)
        except Exception:
            raise Exception("Workflow query has failed")

    def exec_report(self, database, uid, upasswd, report_name,
                    osv_name, obj_id, report_type='pdf'):
        #TODO _ConnectorXMLRPC.exec_report: need to be tested + fix exceptions
        data = {'model': osv_name, 'id': obj_id, 'report_type': report_type}
        try:
            report_id = self.sock_report.report(database, uid, upasswd,
                                                report_name, [obj_id], data)
        except xmlrpclib.Error as exc:
            raise Exception(exc.faultCode)
        state = False
        attempt = 0
        while not state:
            try:
                pdf_data = self.sock_report.report_get(database,
                                                       uid, upasswd, report_id)
            except xmlrpclib.Error as exc:
                raise Exception(unicode(exc.faultString))
            state = pdf_data['state']
            if not state:
                time.sleep(1)
                attempt += 1
            if attempt > 200:
                raise Exception("Download time exceeded, "
                                "the operation has been canceled.")
        return pdf_data


class _ConnectorNetRPC(_Connector):
    """Connector class using NetRPC protocol."""
    #TODO _ConnectorNetRPC, to implement
    def __init__(self, server, port):
        super(_ConnectorNetRPC, self).__init__(server, port)
        raise Exception("NetRPC protocol will be implemented "
                        "in a future release. Stay tuned!")

    def login(self, user, passwd, database=None):
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
