
=======
OERPLib
=======

`OERPLib` is a client library to `OpenERP` server. It aims to provide an easy
way to remotely pilot an `OpenERP` server.

Features supported:
    - XML-RPC and Net-RPC protocols
    - convenient methods such as ``create``, ``read``, ``write``, ``unlink`` and
      ``search`` (alongside ``execute`` to perform other methods),
    - browse records (``browse`` method implemented),
    - execute workflows,
    - manage databases,
    - reports downloading.

How does it work? See below::

    #!/usr/bin/env python
    import oerplib

    # Prepare the connection to the OpenERP server
    oerp = oerplib.OERP('localhost', 'db_name')

    # Login (the object returned is a browsable record)
    user = oerp.login('user', 'passwd')
    print(user.name)            # name of the user connected
    print(user.company_id.name) # the name of its company

    # Simple 'raw' query
    user_data = oerp.execute('res.users', 'read', user.id)
    print(user_data)

    # Or use the 'read' method
    # ('create', 'write', 'unlink' and 'search' exist too)
    user_data = oerp.read('res.users', user.id)

    # Advanced query: get browsable records
    for order in oerp.browse('sale.order', [1, 2]):
        print(order.name)
        for line in order.order_line:
            print(line.name)

    # Update data through a browsable record
    user.name = "Brian Jones"
    oerp.write_record(user)

See the documentation for more details.

Supported OpenERP versions
--------------------------

`OERPLib` is known to work with `OpenERP` server v5 and v6.

Supported Python versions
-------------------------

`OERPLib` support Python versions 2.6 and 2.7.

Generate the documentation
--------------------------

To generate the documentation, you have to install `Sphinx` documentation
generator::

    easy_install -U sphinx

Then, you can use the ``build_doc`` option of the ``setup.py``::

    python setup.py build_doc

The generated documentation will be in the ``./doc/build/html`` directory.

Bugs or suggestions
-------------------

Please, feel free to report bugs or suggestions in the `Bug Tracker
<https://bugs.launchpad.net/oerplib/+filebug>`_!

Changes in this version
-----------------------

Consult the ``CHANGES.txt`` file.

