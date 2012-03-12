#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

import unittest

from args import ARGS

from test_init import TestInit
from test_login import TestLogin
from test_db_create import TestDBCreate
from test_db import TestDB
from test_db_drop import TestDBDrop

if __name__ == '__main__':
    suite = unittest.TestSuite()
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
    # Test OERP.db
    loader = unittest.TestLoader().loadTestsFromTestCase(TestDB)
    suite.addTest(loader)
    # End) Test OERP.db (drop the database)
    if ARGS.create_db and ARGS.drop_db:
        loader = unittest.TestLoader().loadTestsFromTestCase(TestDBDrop)
        suite.addTest(loader)
    else:
        print("-- TestDBDrop skipped --")

    # Run all tests
    unittest.TextTestRunner(verbosity=ARGS.verbosity).run(suite)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
