#!/usr/bin/env python
import oerplib

# XMLRPC server configuration (NETRPC is not supported)
XMLRPC_SERVER = 'localhost'
XMLRPC_SERVER_PORT = 8069
# DMS service configuration
FTP_SERVER = 'localhost'
FTP_SERVER_PORT = 8021
# Name of the OpenERP database to use
DATABASE = 'database-dev'
# Use OpenERP Document Management System module
# (this one must be installed on the server side)
USE_DMS = True

USER = 'admin'
PASSWORD = 'password'

try:
    # Login
    oerp = oerplib.OERP(
            server=XMLRPC_SERVER,
            port=XMLRPC_SERVER_PORT,
            database=DATABASE,
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
    #FIXME

    # Get a report
    pdf_path = oerp.exec_report('sale.order', 'sale.order', 1)

    # --------------------------- #
    # -- Search IDs of objects -- #
    # --------------------------- #

    # Search IDs of a model that match criteria
    assert oerp.user.id in oerp.search('res.users', [('name', 'ilike', u"Administrator"),])

    # ---------------------------- #
    # -- Read data of an object -- #
    # ---------------------------- #
    print(oerp.read('res.users', oerp.user.id))

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

    # ------------------------------- #
    # -- OERP Dictionary interface -- #
    # ------------------------------- #

    # An object may be accessed via a dictionary interface
    print(oerp['res.users'][oerp.user.id].name)

    # Modifications can be saved too
    oerp['res.users'][oerp.user.id].name = u"James Bond"
    oerp.write(oerp['res.users'][oerp.user.id])

    # Changes can be canceled
    oerp['res.users'][oerp.user.id].name = u"Thierry la Fronde"
    oerp.reset(oerp['res.users'][oerp.user.id])
    print(oerp['res.users'][oerp.user.id].name) # Display "James Bond"

    # And they can be updated from Open ERP server
    oerp.refresh(oerp['res.users'][oerp.user.id])

    # Many2One fields can be updated easily (with an ID or with an object)
    oerp['res.users'][oerp.user.id].address_id = oerp.browse('res.partner.address', 1)
    oerp.write(oerp['res.users'][oerp.user.id])
    oerp['res.users'][oerp.user.id].address_id = 1  # ID supplied: same effect as above, implicit relation used
    oerp.write(oerp['res.users'][oerp.user.id])

    # -------------------------------- #
    # -- Document Management System -- #
    # -------------------------------- #

    if USE_DMS:
        # Get a DMS object
        dms = oerplib.DMS(FTP_SERVER, FTP_SERVER_PORT)
        # Login on the DMS
        dms.login(USER, PASSWORD)
        print("---- Content of {0}".format(dms.pwd()))
        dms.dir()
        dms.cwd(DATABASE)
        print("---- Content of {0}".format(dms.pwd()))
        dms.dir()
        dms.cwd('Documents')
        print("---- Content of {0}".format(dms.pwd()))
        dms.dir()
        dms.cwd('Sales Order')
        print("---- Content of {0}".format(dms.pwd()))
        dms.dir()

        dms.cwd('All Sales Order/SO001')
        pdf_path = dms.get('SO001_print.pdf')

except oerplib.error.Error as e:
    print(e)
except Exception as e:
    print(e)

