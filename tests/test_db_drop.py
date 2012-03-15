# -*- coding: UTF-8 -*-

import unittest

from args import ARGS

import oerplib


class TestDBDrop(unittest.TestCase):

    def test_db_drop_existing_database(self):
        oerp = oerplib.OERP(ARGS.server)
        res = oerp.db.drop(ARGS.super_admin_passwd, ARGS.database)
        self.assertTrue(res)
        db_list = oerp.db.list()
        self.assertNotIn(ARGS.database, db_list)

    def test_db_drop_no_existing_database(self):
        #TODO
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
