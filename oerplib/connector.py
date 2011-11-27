# -*- coding: UTF-8 -*-
"""This module provides a connector (via the 'get_connector' method)
which use the XMLRPC or NetRPC protocol to communicate with an OpenERP server.
Here an example of using:

    Get a connector object:
    >>> import connector
    >>> cnt = connector.get_connector('localhost', 8070, 'netrpc')

    Login and retrieve ID of the user connected:
    >>> uid = cnt.login('database', 'user', 'passwd')

    Execute a query:
    >>> res = cnt.execute(uid, 'passwd', 'res.partner', 'read', 42)

    Execute a workflow query:
    >>> res = cnt.exec_workflow(uid, 'passwd', 'sale.order', 'order_confirm', 4)

    Download the data of a report :
    >>> data = cnt.report(uid, 'passwd', 'sale.order', 'sale.order', 4, 'pdf')
"""

import xmlrpclib, socket
import abc
import time

def get_connector(server, port, protocol='xmlrpc'):
    """Return a Connector class to interact with an OpenERP server.
    This one use either the XMLRPC protocol (by default) or NetRPC,
    at the discretion of the user.
    """
    connectors = {
            'xmlrpc': _ConnectorXMLRPC,
            'netrpc': _ConnectorNetRPC,
            }
    if protocol not in connectors:
        error = ("The protocol '{0}' is not supported. "
                "Please choose a protocol among these ones: {1}")
        error = error.format(protocol, connectors.keys())
        raise ProtocolError(error)
    return connectors[protocol](server, port)


class _Connector(object):
    """Connector base class defining the interface used
    to interact with an OpenERP server.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, server, port):
        self.server = server
        self.port = port

    @abc.abstractmethod
    def login(self, database, user, passwd):
        """Log in the user on a database. Return the user's ID.
        Raise a LoginError exception if an error occur.
        """
        pass

    @abc.abstractmethod
    def execute(self, uid, upasswd, osv_name, method, *args, **kwargs):
        """Execute a simple RPC query. Return the result of
        the remote procedure.
        Raise a ExecuteError exception if an error occur.
        """
        pass

    @abc.abstractmethod
    def exec_workflow(self, uid, upasswd, osv_name, signal, obj_id):
        """Execute a RPC workflow query.
        Raise a ExecWorkflowError exception if an error occur.
        """
        pass

    @abc.abstractmethod
    def report(self, uid, upasswd, report_name,
                    osv_name, obj_id, report_type='pdf'):
        """Execute a RPC query to retrieve a report.
        'report_type' can be 'pdf', 'webkit', etc.
        Raise a ExecReportError exception if an error occur.
        """
        pass


class _ConnectorXMLRPC(_Connector):
    """Connector class using XMLRPC protocol."""
    def __init__(self, server, port):
        super(_ConnectorXMLRPC, self).__init__(server, port)
        self.url = 'http://{server}:{port}/xmlrpc'.format(server=self.server,
                                                          port=self.port)
        self.sock_object = xmlrpclib.ServerProxy(self.url+'/object')
        self.sock_report = xmlrpclib.ServerProxy(self.url+'/report')
        self.sock_common = xmlrpclib.ServerProxy(self.url+'/common')

    def login(self, database, user, passwd):
        self.database = database
        try:
            user_id = self.sock_common.login(self.database, user, passwd)
        except xmlrpclib.Fault as exc:
            #NOTE: exc.faultCode is in unicode and Exception doesn't
            # handle unicode object
            raise LoginError(repr(exc.faultCode))
        except socket.error as exc:
            raise LoginError(exc.strerror)
        else:
            return user_id

    def execute(self, uid, upasswd, osv_name, method, *args, **kwargs):
        try:
            return self.sock_object.execute(self.database, uid, upasswd,
                                            osv_name, method, *args, **kwargs)
        except xmlrpclib.Error as exc:
            raise ExecuteError("{0}: {1}".format(
                                            exc.faultCode or "Unknown error",
                                            exc.faultString))

    def exec_workflow(self, uid, upasswd, osv_name, signal, obj_id):
        try:
            return self.sock_object.exec_workflow(self.database, uid, upasswd,
                                                  osv_name, signal, obj_id)
        except Exception:
            raise ExecWorkflowError("Workflow query has failed.")

    def report(self, uid, upasswd, report_name,
               osv_name, obj_id, report_type='pdf', context=None):
        if context is None:
            context = {}
        data = {'model': osv_name, 'id': obj_id, 'report_type': report_type}
        try:
            report_id = self.sock_report.report(self.database, uid, upasswd,
                                                report_name, [obj_id],
                                                data, context)
        except xmlrpclib.Error as exc:
            raise ExecReportError(exc.faultCode)
        state = False
        attempt = 0
        while not state:
            try:
                pdf_data = self.sock_report.report_get(self.database,
                                                       uid, upasswd, report_id)
            except xmlrpclib.Error as exc:
                raise ExecReportError("Unknown error occurred during the "
                                      "download of the report.")
            state = pdf_data['state']
            if not state:
                time.sleep(1)
                attempt += 1
            if attempt > 200:
                raise ExecReportError("Download time exceeded, "
                                      "the operation has been canceled.")
        return pdf_data


class _ConnectorNetRPC(_Connector):
    """Connector class using NetRPC protocol."""
    #TODO _ConnectorNetRPC, to implement
    def __init__(self, server, port):
        super(_ConnectorNetRPC, self).__init__(server, port)
        raise Exception("NetRPC protocol will be implemented "
                        "in a future release. Stay tuned!")

    def login(self, database, user, passwd):
        self.database = database
        pass

    def execute(self, uid, upasswd, osv_name, method, *args, **kwargs):
        pass

    def exec_workflow(self, uid, upasswd, osv_name, signal, obj_id):
        pass

    def report(self, uid, upasswd, report_name,
               osv_name, obj_id, report_type='pdf', context=None):
        pass


#===========
# Exceptions
#===========

class ProtocolError(BaseException):
    """Exception raised if the protocol supplied
    does not exist/is not supported.
    """
    pass


class LoginError(BaseException):
    """Exception raised during a user login."""
    pass


class ExecuteError(BaseException):
    """Exception raised during a 'execute' query."""
    pass


class ExecWorkflowError(BaseException):
    """Exception raised during a 'exec_workflow' query."""
    pass


class ExecReportError(BaseException):
    """Exception raised during a 'exec_report' query."""
    pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
