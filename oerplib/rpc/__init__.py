from oerplib.rpc import connector, error

PROTOCOLS = {
        'xmlrpc': connector.ConnectorXMLRPC,
        'netrpc': connector.ConnectorNetRPC,
        }

def get_connector(server, port, protocol='xmlrpc'):
    """Return a `RPC` connector to interact with an `OpenERP` server.
    This one use either the `XML-RPC` protocol (by default) or `Net-RPC`,
    at the discretion of the user.
    """
    if protocol not in PROTOCOLS:
        txt = ("The protocol '{0}' is not supported. "
               "Please choose a protocol among these ones: {1}")
        txt = txt.format(protocol, PROTOCOLS.keys())
        raise error.ConnectorError(txt)
    return PROTOCOLS[protocol](server, port)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
