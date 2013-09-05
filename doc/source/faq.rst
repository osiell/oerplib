.. _faq:

Frequently Asked Questions (FAQ)
================================

How to connect to an OpenERP Online (SaaS) instance?
----------------------------------------------------

First, you have to connect on your `OpenERP` instance, and set a password for
your user account in order to active the `XML-RPC` protocol.

Then, just use the ``xmlrpc+ssl`` protocol with the port 443::

    >>> import oerplib
    >>> oerp = oerplib.OERP('my-server.my.openerp.com', protocol='xmlrpc+ssl', port=443)
    >>> oerp.db.server_version()
    '7.saas~1'
