# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import oerplib


class TestInspect(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.user = self.oerp.login(ARGS.user, ARGS.passwd, ARGS.database)

    def test_relations(self):
        res = self.oerp.inspect.relations(
            ['res.users'],
            maxdepth=1,
            whitelist=['*'], blacklist=[],
            attrs_whitelist=['*'], attrs_blacklist=[])
        self.assertIsInstance(res, oerplib.service.inspect.relations.Relations)

    def test_scan_on_change(self):
        res = self.oerp.inspect.scan_on_change(['res.users'])
        self.assertIsInstance(res, dict)
        res = self.oerp.inspect.scan_on_change(['res.users', 'res.partner'])
        self.assertIsInstance(res, dict)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
