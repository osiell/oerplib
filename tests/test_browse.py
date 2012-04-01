# -*- coding: UTF-8 -*-

import unittest

from args import ARGS

import oerplib


class TestBrowse(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(ARGS.server, ARGS.database,
                                 protocol=ARGS.protocol, port=ARGS.port)
        self.user = self.oerp.login(ARGS.user, ARGS.passwd)

    def test_browse_with_one_id(self):
        # Check the result returned
        result = self.oerp.browse('res.users', self.user.id)
        self.assertIsInstance(result, oerplib.service.osv.browse.BrowseRecord)
        self.assertEqual(self.user, result)
        # With context
        context = self.oerp.execute('res.users', 'context_get')
        result = self.oerp.browse('res.users', self.user.id, context)
        self.assertIsInstance(result, oerplib.service.osv.browse.BrowseRecord)
        self.assertEqual(self.user, result)

    def test_browse_with_ids(self):
        # Iteration
        for result in self.oerp.browse('res.users', [self.user.id]):
            self.assertEqual(self.user, result)
        user_ids = self.oerp.search('res.users', [])
        for result in self.oerp.browse('res.users', user_ids):
            self.assertIsInstance(
                    result, oerplib.service.osv.browse.BrowseRecord)
        # With context
        context = self.oerp.execute('res.users', 'context_get')
        for result in self.oerp.browse('res.users', user_ids, context):
            self.assertIsInstance(
                    result, oerplib.service.osv.browse.BrowseRecord)

    def test_browse_without_args(self):
        # Handle exception (execute a 'browse' without args)
        self.assertRaises(
                TypeError,
                self.oerp.browse,
                'res.users')

    def test_browse_with_wrong_args(self):
        # Handle exception (execute a 'browse' with wrong args)
        self.assertRaises(
                oerplib.error.RPCError,
                self.oerp.browse,
                'res.users',
                False) # Wrong arg

    def test_write_record(self):
        # Check the result returned
        backup_name = self.user.name
        self.user.name = "Charly"
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.name, "Charly")
        self.user.name = backup_name
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.name, backup_name)

    def test_reset(self):
        # Check the result returned
        self.user.name = "Charly"
        self.oerp.reset(self.user)
        self.assertEqual(self.user.name, "Administrator")

    def test_refresh(self):
        # Check the result returned
        self.user.name = "Charly"
        self.oerp.refresh(self.user)
        self.assertEqual(self.user.name, "Administrator")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
