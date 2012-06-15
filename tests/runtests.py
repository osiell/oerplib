#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

import unittest

from args import ARGS

from test_init import TestInit
from test_login import TestLogin
from test_db_create import TestDBCreate
from test_db import TestDB
from test_db_drop import TestDBDrop
from test_execute import TestExecute
from test_browse import TestBrowse
from test_osv import TestOSV

if __name__ == '__main__':
    suite = unittest.TestSuite()

    #---------------
    #- First Tests -
    #---------------

    # 1) Test OERP.__init__
    loader = unittest.TestLoader().loadTestsFromTestCase(TestInit)
    suite.addTest(loader)
    # 2) Test OERP.db (create the database)
    if ARGS.create_db:
        loader = unittest.TestLoader().loadTestsFromTestCase(TestDBCreate)
        suite.addTest(loader)
    else:
        print("-- TestDBCreate skipped --")
    # 3) Test OERP.login
    loader = unittest.TestLoader().loadTestsFromTestCase(TestLogin)
    suite.addTest(loader)

    #---------
    #- Tests -
    #---------

    # Test OERP.db
    loader = unittest.TestLoader().loadTestsFromTestCase(TestDB)
    suite.addTest(loader)

    # Test OERP.execute
    loader = unittest.TestLoader().loadTestsFromTestCase(TestExecute)
    suite.addTest(loader)

    # Test OERP.browse
    loader = unittest.TestLoader().loadTestsFromTestCase(TestBrowse)
    suite.addTest(loader)

    # Test OERP.get
    loader = unittest.TestLoader().loadTestsFromTestCase(TestOSV)
    suite.addTest(loader)

    #---------------
    #- Final Tests -
    #---------------

    # Test OERP.db (drop the database)
    if ARGS.create_db and ARGS.drop_db:
        loader = unittest.TestLoader().loadTestsFromTestCase(TestDBDrop)
        suite.addTest(loader)
    else:
        print("-- TestDBDrop skipped --")

    # Run all tests
    if ARGS.test_xmlrpc:
        print("-- RUN (XMLRPC) --")
        ARGS.protocol = 'xmlrpc'
        ARGS.port = ARGS.xmlrpc_port
        unittest.TextTestRunner(verbosity=ARGS.verbosity).run(suite)
    if ARGS.test_netrpc:
        print("-- RUN (NETRPC) --")
        ARGS.protocol = 'netrpc'
        ARGS.port = ARGS.netrpc_port
        unittest.TextTestRunner(verbosity=ARGS.verbosity).run(suite)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
