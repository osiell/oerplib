
class ConnectorError(BaseException):
    """Exception raised if the informations supplied
    to initiate the connector are wrong.
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
