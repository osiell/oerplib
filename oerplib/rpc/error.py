# -*- coding: UTF-8 -*-

class ConnectorError(BaseException):
    """Exception raised by the ``oerplib.rpc`` package."""
    def __init__(self, message, oerp_traceback=None):
        self.message = message
        self.oerp_traceback = oerp_traceback

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
