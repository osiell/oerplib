#!/usr/bin/env python
"""A sample script to demonstrate some of functionalities of OERPLib."""
import oerplib

# XMLRPC server configuration (NETRPC is also supported)
SERVER = 'localhost'
PROTOCOL = 'xmlrpc'
PORT = 8069
# Name of the OpenERP database to use
DATABASE = 'db_name'

USER = 'admin'
PASSWORD = 'password'

try:
    # Login
    oerp = oerplib.OERP(
            server=SERVER,
            database=DATABASE,
            protocol=PROTOCOL,
            port=PORT,
            )
    oerp.login(USER, PASSWORD)

    # ----------------------- #
    # -- Low level methods -- #
    # ----------------------- #

    # Execute - search
    user_ids = oerp.execute('res.users', 'search', [('id', '=', oerp.user.id)])

    # Execute - read
    user_data = oerp.execute('res.users', 'read', user_ids[0])

    # Execute - write
    oerp.execute('res.users', 'write', user_ids[0], {'name': u"Administrator"})

    # Execute - create
    new_user_id = oerp.execute('res.users', 'create', {'login': u"New user"})

    # ------------------------- #
    # -- Convenients methods -- #
    # ------------------------- #

    # Search IDs of a model that match criteria
    assert oerp.user.id in oerp.search('res.users', [('name', 'ilike', u"Administrator"),])

    # Create a record
    new_user_id = oerp.create('res.users', {'login': u"new_user"})

    # Read data of a record
    user_data = oerp.read('res.users', new_user_id)

    # Write a record
    oerp.write('res.users', [new_user_id], {'name': u"New user"})

    # Delete a record
    oerp.unlink('res.users', new_user_id)

    # -------------------- #
    # -- Browse objects -- #
    # -------------------- #

    # Browse an object
    user = oerp.browse('res.users', oerp.user.id)
    print(user.name)
    print(user.company_id.name)

    # .. or many objects
    for order in oerp.browse('sale.order', [68, 69]):
        print(order.name)
        print(order.partner_id.name)
        for line in order.order_line:
            print('\t{0}'.format(line.name))

    # ----------------------- #
    # -- Download a report -- #
    # ----------------------- #

    so_pdf_path = oerp.report('sale.order', 'sale.order', 1)
    inv_pdf_path = oerp.report('webkitaccount.invoice', 'account.invoice', 1)

    # -------------------- #
    # -- List databases -- #
    # -------------------- #

    # List databases
    print(oerp.db.list())

    # Create a database in background
    oerp.db.create(
            super_admin_passwd='super_admin_passwd',
            database='my_new_db',
            demo_data=True, lang='fr_FR',
            admin_passwd='admin_passwd')

    # Create a database (process blocked until the end of the operation)
    oerp.db.create_and_wait(
            super_admin_passwd='super_admin_passwd',
            database='my_new_db',
            demo_data=True, lang='fr_FR',
            admin_passwd='admin_passwd')

except oerplib.error.Error as e:
    print(e)
except Exception as e:
    print(e)

