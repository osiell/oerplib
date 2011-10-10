.. _tutorials:

Tutorials
=========

First step: prepare the connection and login
--------------------------------------------

You need an instance of the :class:`OERP <oerplib.OERP>` class to dialog with an
`OpenERP` server. Let's pretend that you want to connect as `admin` on the
`db_name` database of the local `OpenERP` server (with the `XML-RPC` service
which listens on port 8071). First, prepare the connection::

    >>> import oerplib
    >>> oerp = oerplib.OERP(server='localhost', port=8071)

You can also specify the default database to use with the `database` parameter::

    >>> oerp = oerplib.OERP(server='localhost', database='db_name', port=8071)

The connection is ready, you can now login to the server with the account of
your choice::

    >>> user = oerp.login(user='admin', passwd='admin')

Or, if no default database was specified::

    >>> user = oerp.login(user='admin', passwd='admin', database='db_name')

The ``login`` method returns an object representing the user connected.
It is built from the server-side OSV model ``res.users``, and all its
informations are accessible (see :ref:`browse-objects` section)::

    >>> print(user.name)            # print the full name of the user
    >>> print(user.company_id.name) # print the name of its company

Now you are connected, you can easily execute XML-RPC queries and handle all OSV
classes from the `OpenERP` server.

Execute queries
---------------

The basic method to execute queries is ``execute``. It takes at least two
parameters (OSV class name and the method name) following by variable parameters
according to the method called. Example::

    >>> user_data = oerp.execute('sale.order', 'read', 1)

This instruction will call the ``read`` method of the OSV class ``sale.order``
with the parameter ``1`` (the ID record asked by ``read``).

For standard OSV methods suscribed to the XML-RPC service like ``create``,
``read``, ``write``, ``unlink`` and ``search``, convenient methods exist::

    >>> partner_id = oerp.create('res.partner', {'name': 'Jacky Bob', 'lang': 'fr_FR'})
    >>> partner_data = oerp.read('res.partner', partner_id)
    >>> oerp.write('res.partner', [partner_id], {'name': 'Charly Bob'})
    >>> partner_ids = oerp.search('res.partner', [('name', 'ilike', 'Bob')])
    >>> oerp.unlink('res.partner', [partner_id])

.. _browse-objects:

Browse objects
--------------

The main functionality of `OERPLib` is its ability to generate objects that are
similar to browsable objects that can be found on the `OpenERP` server. All this
is possible using the ``browse`` method::

    # fetch one object
    partner = oerp.browse('res.partner', 1) # Partner ID = 1
    print(partner.name)
    # fetch several objects
    for partner in oerp.browse('res.partner', [1, 2]):
        print(partner.name)

From such objects, it is possible to easily explore relationships. The related
objects are generated on the fly::

    for addr in partner.address:
        print(addr.name)

Outside relation fields, Python data types are used, like ``datetime.date`` and
``datetime.datetime``::

    >>> order = oerp.browse('purchase.order', 42)
    >>> order.minimum_planned_date
    datetime.datetime(2010, 5, 29, 0, 0)
    >>> order.date_order
    datetime.date(2010, 5, 27)

.. See the table of equivalents types with `OpenERP`.

Update data through browsable objects
-------------------------------------

Update data of a browsable object is workable with the ``write`` method of an
:class:`OERP <oerplib.OERP>` instance. Let's update the first contact's name of
a partner::

    >>> partner.address[0].name = "Caporal Jones"
    >>> oerp.write(partner.address[0])

This is equivalent to::

    >>> addr_osv_name = oerp.get_osv_name(partner.address[0]) # 'res.partner.address'
    >>> addr_id = partner.address[0].id
    >>> oerp.write(addr_osv_name, [addr_id], {'name': "Caporal Jones"})

Nowadays, update operation through browsable objects doesn't support
``one2many`` and ``many2many`` fields.

Char, Float, Integer, Boolean, Text and Binary
''''''''''''''''''''''''''''''''''''''''''''''

As see above, it's as simple as that::

    >>> partner.name = "OpenERP"
    >>> oerp.write(partner)

Selection
'''''''''

Same as above, except there is a check about the value assigned. For example,
the field ``type`` of the ``res.partner.address`` model accept values contains
in ``['default', 'invoice', 'delivery', 'contact', 'other']``::

    >>> my_partner_address.type = 'default' # Ok
    >>> my_partner_address.type = 'foobar'  # Error!
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "oerplib/fields.py", line 58, in setter
        value = self.check_value(value)
      File "oerplib/fields.py", line 73, in check_value
        field_name=self.name,
    ValueError: The value 'foobar' supplied doesn't match with the possible values '['default', 'invoice', 'delivery', 'contact', 'other']' for the 'type' field

Many2One
''''''''

You can also update a ``many2one`` field, with either an ID or a browsable
object::

    >>> addr.partner_id = 42 # with an ID
    >>> oerp.write(addr)
    >>> partner = oerp.browse('res.partner', 42) # with a browsable object
    >>> addr.partner_id = partner
    >>> oerp.write(addr)

You can't put any ID or browsable object, a check is made on the relationship
to ensure data integrity::

    >>> user = oerp.browse('res.users', 1)
    >>> addr = oerp.browse('res.partner.address', 1)
    >>> addr.partner_id = user
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "oerplib/fields.py", line 128, in setter
        o_rel = self.check_value(o_rel)
      File "oerplib/fields.py", line 144, in check_value
        field_name=self.name))
    ValueError: Instance of 'res.users' supplied doesn't match with the relation 'res.partner' of the 'partner_id' field.

Date and Datetime
'''''''''''''''''

``date`` and ``datetime`` fields accept either string values or
``datetime.date/datetime.datetime`` objects.

With ``datetime.date`` and ``datetime.datetime`` objects::

    >>> order = oerp.browse('purchase.order', 42)
    >>> order.date_order = datetime.date(2011, 9, 20)
    >>> order.minimum_planned_date = datetime.datetime(2011, 9, 20, 12, 31, 24)
    >>> oerp.write(order)

With formated strings::

    >>> order.date_order = "2011-09-20"                     # %Y-%m-%d
    >>> order.minimum_planned_date = "2011-09-20 12:31:24"  # %Y-%m-%d %H:%M:%S
    >>> oerp.write(order)

As always, a wrong type will raise an exception::

    >>> order.date_order = "foobar"
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "oerplib/fields.py", line 187, in setter
        value = self.check_value(value)
      File "oerplib/fields.py", line 203, in check_value
        self.pattern))
    ValueError: Value not well formatted, expecting '%Y-%m-%d' format

