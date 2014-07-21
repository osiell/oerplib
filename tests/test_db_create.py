# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import oerplib
from oerplib.tools import v


class TestDBCreate(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)

    def test_db_create(self):
        if ARGS.database not in self.oerp.db.list():
            if v(self.oerp.version) >= v('8.0'):
                res = self.oerp.db.create_database(
                    ARGS.super_admin_passwd,
                    ARGS.database,
                    False,
                    'en_US',
                    ARGS.passwd)
                self.assertTrue(res)
            else:
                res = self.oerp.db.create_and_wait(
                    ARGS.super_admin_passwd,
                    ARGS.database,
                    False,
                    'en_US',
                    ARGS.passwd)
                self.assertIsInstance(res, list)
                self.assertNotEqual(res, list())
                self.assertEqual(res[0]['login'], 'admin')
                self.assertEqual(res[0]['password'], ARGS.passwd)
            import time
            time.sleep(10)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
