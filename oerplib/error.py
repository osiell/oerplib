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


class RPCError(Error):
    """Exception raised when an error related to a RPC query occurs."""
    pass


class InternalError(Error):
    """Exception raised when an error occurred during an internal operation."""
    pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
