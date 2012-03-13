oerplib.OERP
============

.. autoclass:: oerplib.OERP
    :members:


Field types
-----------

The table below presents the Python types returned by `OERPLib`
for each `OpenERP` fields:

================  ==============================
`OpenERP` fields  Python types used in `OERPLib`
================  ==============================
fields.binary     basestring (str or unicode)
fields.boolean    bool
fields.char       basestring (str or unicode)
fields.date       datetime.date
fields.datetime   datetime.datetime
fields.float      float
fields.integer    integer
fields.selection  basestring (str or unicode)
fields.text       basestring (str or unicode)
================  ==============================

Exceptions made for relation fields:

================  ===========================================================
`OpenERP` fields  Types used in `OERPLib`
================  ===========================================================
fields.many2one   ``oerplib.service.osv.browse.BrowseRecord`` object
fields.one2many   list of ``oerplib.service.osv.browse.BrowseRecord`` objects
fields.many2many  list of ``oerplib.service.osv.browse.BrowseRecord`` objects
================  ===========================================================

