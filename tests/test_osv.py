# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import oerplib


class TestOSV(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.user = self.oerp.login(ARGS.user, ARGS.passwd, ARGS.database)

    def test_osv(self):
        # Check the result returned
        self.oerp.get('res.users')

    def test_osv_method(self):
        # Check the result returned
        osv_class = self.oerp.get('res.users')
        osv_class.name_get(self.user.id)

    def test_osv_method_without_args(self):
        # Handle exception (execute a 'name_get' with without args)
        osv_class = self.oerp.get('res.users')
        self.assertRaises(
            oerplib.error.RPCError,
            osv_class.name_get)

    def test_osv_method_with_wrong_args(self):
        # Handle exception (execute a 'search' with wrong args)
        osv_class = self.oerp.get('res.users')
        self.assertRaises(
            oerplib.error.RPCError,
            osv_class.search,
            False)  # Wrong arg

    def test_osv_browse_with_one_id(self):
        # Check the result returned
        osv_class = self.oerp.get('res.users')
        user = osv_class.browse(self.user.id)
        self.assertEqual(user, self.user)

    def test_osv_browse_with_ids(self):
        # Iteration
        for result in self.oerp.get('res.users').browse([self.user.id]):
            self.assertEqual(self.user, result)
        user_ids = self.oerp.search('res.users', [])
        for result in self.oerp.get('res.users').browse(user_ids):
            self.assertIsInstance(
                result, oerplib.service.osv.browse.BrowseRecord)
        # With context
        context = self.oerp.execute('res.users', 'context_get')
        for result in self.oerp.get('res.users').browse(user_ids, context):
            self.assertIsInstance(
                result, oerplib.service.osv.browse.BrowseRecord)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
