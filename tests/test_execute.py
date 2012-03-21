# -*- coding: UTF-8 -*-

import unittest
import numbers

from args import ARGS

import oerplib


class TestExecute(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(ARGS.server, ARGS.database,
                                 protocol=ARGS.protocol, port=ARGS.port)
        self.user = self.oerp.login(ARGS.user, ARGS.passwd)

    # ------
    # Search
    # ------
    def test_execute_search_with_good_args(self):
        # Check the result returned
        result = self.oerp.execute('res.users', 'search', [])
        self.assertIsInstance(result, list)
        self.assertIn(self.user.id, result)
        result = self.oerp.execute('res.users', 'search',
                                   [('id', '=', self.user.id)])
        self.assertIn(self.user.id, result)
        self.assertEqual(result[0], self.user.id)

    def test_execute_search_without_args(self):
        # Handle exception (execute a 'search' without args)
        self.assertRaises(
                oerplib.error.RPCError,
                self.oerp.execute,
                'res.users',
                'search')

    def test_execute_search_with_wrong_args(self):
        # Handle exception (execute a 'search' with wrong args)
        self.assertRaises(
                oerplib.error.RPCError,
                self.oerp.execute,
                'res.users',
                'search',
                False) # Wrong arg

    # ------
    # Create
    # ------
    def test_execute_create_with_good_args(self):
        # Check the result returned
        result = self.oerp.execute(
                'res.users', 'create',
                {'name': "Foobar",
                 'login': 'foo'})
        self.assertIsInstance(result, numbers.Number)
        # Handle exception (create another user with the same login)
        self.assertRaises(
                oerplib.error.RPCError,
                self.oerp.execute,
                'res.users', 'create',
                {'name': "Foobar", 'login': 'foo'})

    def test_execute_create_without_args(self):
        # Handle exception (execute a 'create' without args)
        self.assertRaises(
                oerplib.error.RPCError,
                self.oerp.execute,
                'res.users',
                'create')

    def test_execute_create_with_wrong_args(self):
        # Handle exception (execute a 'create' with wrong args)
        self.assertRaises(
                oerplib.error.RPCError,
                self.oerp.execute,
                'res.users',
                'create',
                False) # Wrong arg

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
