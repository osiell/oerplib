# -*- coding: UTF-8 -*-
"""This module contains all exceptions raised by `OERPLib` when an error
occurred.

"""


class Error(Exception):
    def __init__(self, message, oerp_traceback=False):
        super(Error, self).__init__()
        self.message = message
        self.oerp_traceback = oerp_traceback

    def __str__(self):
        return u"{message}".format(message=self.message)


class RPCError(Error):
    """Exception raised when an error related to a RPC query occurs."""
    pass


class InternalError(Error):
    """Exception raised when an error occurred during an internal operation."""
    pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
