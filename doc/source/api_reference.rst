Reference
=========

.. automodule:: oerplib
    :members:

Here's a sample session using this module::

    >>> import oerplib
    >>> oerp = oerplib.OERP('localhost')                    # connect to localhost, default port
    >>> user = oerp.login('admin', 'admin', 'my_database')  # login returns an user object
    >>> user.name
    'Administrator'

OERP Class
----------

.. autoclass:: OERP
    :members:


Field types
-----------

The table below presents the Python types used for each `OpenERP` fields:

================  ==============================
`OpenERP` fields  Python types used in `OERPLib`
================  ==============================
fields.binary     ?
fields.boolean    bool
fields.char       basestring
fields.date       datetime.date
fields.datetime   datetime.datetime
fields.float      float
fields.integer    integer
fields.selection  basestring (str or unicode)
fields.text       basestring (str or unicode)
================  ==============================

Exceptions made for relation fields:

================  ===============================================
`OpenERP` fields  Types used in `OERPLib`
================  ===============================================
fields.many2one   ``oerplib.browse.BrowseRecord`` object
fields.one2many   list of ``oerplib.browse.BrowseRecord`` objects
fields.many2many  list of ``oerplib.browse.BrowseRecord`` objects
================  ===============================================

Exceptions
----------

.. automodule:: oerplib.error
    :members:

