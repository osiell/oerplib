# -*- coding: UTF-8 -*-

import unittest

from args import ARGS

import oerplib


class TestBrowse(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(ARGS.server, ARGS.database,
                                 protocol=ARGS.protocol, port=ARGS.port)
        self.user = self.oerp.login(ARGS.user, ARGS.passwd)

    def test_browse_with_good_args(self):
        # Check the result returned
        result = self.oerp.browse('res.users', self.user.id)
        self.assertIsInstance(result, oerplib.service.osv.browse.BrowseRecord)
        self.assertEqual(self.user, result)
        # Iteration
        for result in self.oerp.browse('res.users', [self.user.id]):
            self.assertEqual(self.user, result)
        # With context
        context = self.oerp.execute('res.users', 'context_get', self.user.id)
        result = self.oerp.browse('res.users', self.user.id, context)
        self.assertIsInstance(result, oerplib.service.osv.browse.BrowseRecord)
        self.assertEqual(self.user, result)

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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
