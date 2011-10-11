
=======
OERPLib
=======

`OERPLib` is a client library to OpenERP server. It aims to provide an easy way
to remotely pilot an `OpenERP` server.
In addition to supporting ``create``, ``read``, ``write``, ``unlink`` and
``search`` operations, this library is also able to generate objects which are
somewhat similar to the browsable objects available on OpenERP server via the
implementation of the ``browse`` method, and manipulate them while hiding
XML-RPC queries.
Retrieve reports and execute workflow queries are also possible.

How does it work? See below::

    #!/usr/bin/env python
    import oerplib

    # Prepare the connection to the OpenERP server
    oerp = oerplib.OERP('localhost', 'db_name')

    # Login
    user = oerp.login('user', 'passwd')
    print(user.name)            # name of the user connected
    print(user.company_id.name) # the name of its company

    # Simple 'raw' query
    user_data = oerp.execute('res.users', 'read', user.id)
    print(user_data)

    # Or use the 'read' method
    # ('create', 'write', 'unlink' and 'search' exist too)
    user_data = oerp.read('res.users', user.id)

    # Advanced query: browse objects!
    for order in oerp.browse('sale.order', [1, 42]):
        print(order.name)
        for line in order.order_line:
            print(line.name)

    # Update data through a browsable object
    order.name = "NEW ORDER REF"
    oerp.write(order)

See the documentation for more details.

Supported OpenERP versions
--------------------------

OERPLib is known to work with OpenERP server v5 and v6.

Generate the documentation
--------------------------

To generate the documentation, you have to install Sphinx documentation
generator::

    easy_install -U sphinx

Now, you can use the ``build_sphinx`` option of the ``setup.py``::

    python setup.py build_sphinx

The generated documentation will be in the ``./doc/html`` directory.

Bugs or suggestions
-------------------

Please, feel free to report bugs or suggestions in the `Bug Tracker
<https://bitbucket.org/SebAlix/python-oerplib/issues?status=new&status=open>`_!

Changes in this version
-----------------------

Consult the ``CHANGES.txt`` file.

