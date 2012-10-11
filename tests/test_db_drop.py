# -*- coding: UTF-8 -*-

import unittest

from args import ARGS

import oerplib


class TestDBDrop(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(ARGS.server,
                                 protocol=ARGS.protocol, port=ARGS.port)

    def test_db_drop_existing_database(self):
        res = self.oerp.db.drop(ARGS.super_admin_passwd, ARGS.database)
        self.assertTrue(res)
        db_list = self.oerp.db.list()
        self.assertNotIn(ARGS.database, db_list)

    def test_db_drop_no_existing_database(self):
        version = float(self.oerp.db.server_version()[:3])
        if version >= 6.1:
            res = self.oerp.db.drop(ARGS.super_admin_passwd, 'fake_db_name')
            self.assertFalse(res)
        else:
            self.assertRaises(
                oerplib.error.RPCError,
                self.oerp.db.drop,
                ARGS.super_admin_passwd, 'fake_db_name')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
