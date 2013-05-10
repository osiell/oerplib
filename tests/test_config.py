# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest
import tempfile
import os

from args import ARGS

import oerplib


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.user = self.oerp.login(ARGS.user, ARGS.passwd, ARGS.database)
        self.config_name = ARGS.database
        self.file_path = tempfile.mkstemp(suffix='.cfg', prefix='oerplib_')[1]

    def tearDown(self):
        os.remove(self.file_path)

    def test_config_list(self):
        result = oerplib.config.list(rc_file=self.file_path)
        self.assertIsInstance(result, list)
        other_file_path = tempfile.mkstemp()[1]
        result = oerplib.config.list(rc_file=other_file_path)
        self.assertIsInstance(result, list)

    def test_config_save_and_remove(self):
        self.oerp.save(self.config_name, rc_file=self.file_path)
        result = oerplib.config.list(rc_file=self.file_path)
        self.assertIn(self.config_name, result)
        oerplib.config.remove(self.config_name, rc_file=self.file_path)

    def test_config_get(self):
        self.oerp.save(self.config_name, rc_file=self.file_path)
        data = {
            'server': self.oerp.server,
            'protocol': self.oerp.protocol,
            'port': int(self.oerp.port),
            'timeout': self.oerp.config['timeout'],
            'user': self.oerp.user.login,
            'passwd': self.oerp._password,
            'database': self.oerp.database,
        }
        result = oerplib.config.get(self.config_name, rc_file=self.file_path)
        self.assertEqual(data, result)
        oerplib.config.remove(self.config_name, rc_file=self.file_path)

    def test_config_get_all(self):
        self.oerp.save(self.config_name, rc_file=self.file_path)
        data = {
            self.config_name: {
                'server': self.oerp.server,
                'protocol': self.oerp.protocol,
                'port': int(self.oerp.port),
                'timeout': self.oerp.config['timeout'],
                'user': self.oerp.user.login,
                'passwd': self.oerp._password,
                'database': self.oerp.database,
            }
        }
        result = oerplib.config.get_all(rc_file=self.file_path)
        self.assertIn(self.config_name, result)
        self.assertEqual(data, result)
        oerplib.config.remove(self.config_name, rc_file=self.file_path)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
