# -*- coding: UTF-8 -*-
"""This module contains all Exception classes to manage errors.
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


class DMSConnectionError(Error):
    pass


class LoginError(Error):
    pass


class ExecuteQueryError(Error):
    pass


class WorkflowQueryError(Error):
    pass


class ReportError(Error):
    pass


class NotAllowedError(Error):
    def __init__(self, message):
        super(NotAllowedError, self).__init__(message)


class UnknownError(Error):
    def __init__(self, message):
        super(UnknownError, self).__init__(message)

