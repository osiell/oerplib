# -*- coding: UTF-8 -*-
"""This module contains all exceptions raised by `OERPLib` when an error
occurred.

"""
#import traceback, sys


class Error(Exception):
    def __init__(self, message, oerp_traceback=False):
        super(Error, self).__init__()
        self.oerp_traceback = oerp_traceback
        self.message = message
        #self.tb = sys.exc_info()[2]
    def __str__(self):
        #traceback.print_tb(self.tb)
        return u"{message}".format(message=self.message)


class LoginError(Error):
    """Exception raised when an error occurred during a login operation."""
    pass


class ExecuteQueryError(Error):
    """Exception raised when an error occurred during an execute query."""
    pass


class WorkflowQueryError(Error):
    """Exception raised when an error occurred during an workflow query."""
    pass


class ReportError(Error):
    """Exception raised when an error occurred during a retrieval
    report operation.
    """
    pass


class InternalError(Error):
    """Exception raised when an error occurred during an internal operation."""
    pass


class NotAllowedError(Error):
    """Exception raised if a prohibited operation is made."""
    def __init__(self, message):
        super(NotAllowedError, self).__init__(message)


class UnknownError(Error):
    """Exception raised when an unknown error occurred."""
    def __init__(self, message):
        super(UnknownError, self).__init__(message)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
