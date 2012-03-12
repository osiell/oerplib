
import unittest

import oerplib
from oerplib.service import osv

SERVER = '192.168.1.10'
PROTOCOL = 'xmlrpc'
PORT = 8069
USER = 'admin'
PASSWD = 'admin'
DATABASE = 'oerplib-test'

class TestOERP(unittest.TestCase):

    #def setUp(self):
    #    self.server = SERVER
    #    self.user = USER
    #    self.passwd = PASSWD
    #    self.database = DATABASE

    def test_init(self):
        # Server
        oerp = oerplib.OERP(SERVER)
        self.assertIsInstance(oerp, oerplib.OERP)
        self.assertIsNotNone(oerp)
        self.assertEqual(oerp.server, SERVER)
        self.assertIsNone(oerp.database)
        # Server + Database
        oerp = oerplib.OERP(SERVER, DATABASE)
        self.assertIsInstance(oerp, oerplib.OERP)
        self.assertIsNotNone(oerp)
        self.assertEqual(oerp.server, SERVER)
        self.assertEqual(oerp.database, DATABASE)
        # Server + Database + Protocol
        oerp = oerplib.OERP(SERVER, DATABASE, PROTOCOL)
        self.assertIsInstance(oerp, oerplib.OERP)
        self.assertIsNotNone(oerp)
        self.assertEqual(oerp.server, SERVER)
        self.assertEqual(oerp.database, DATABASE)
        self.assertEqual(oerp.protocol, PROTOCOL)
        # Server + Database + Protocol + Port
        oerp = oerplib.OERP(SERVER, DATABASE, PROTOCOL, PORT)
        self.assertIsInstance(oerp, oerplib.OERP)
        self.assertIsNotNone(oerp)
        self.assertEqual(oerp.server, SERVER)
        self.assertEqual(oerp.database, DATABASE)
        self.assertEqual(oerp.protocol, PROTOCOL)
        self.assertEqual(oerp.port, PORT)

    def test_login(self):
        oerp = oerplib.OERP(SERVER)
        user = oerp.login(USER, PASSWD, DATABASE)
        self.assertIsNotNone(user)
        self.assertIsInstance(user, osv.BrowseRecord)
        self.assertEqual(oerp.user, user)

        oerp = oerplib.OERP(SERVER, DATABASE)
        user = oerp.login(USER, PASSWD)
        self.assertIsNotNone(user)
        self.assertIsInstance(user, osv.BrowseRecord)
        self.assertEqual(oerp.user, user)

    def test_execute(self):
        oerp = oerplib.OERP(SERVER, DATABASE)
        oerp.login(USER, PASSWD)
        # Handle exception (execute a 'search' without args)
        self.assertRaises(
                oerplib.error.ExecuteQueryError,
                oerp.execute,
                'res.users',
                'search')

    def test_search(self):
        oerp = oerplib.OERP(SERVER, DATABASE)
        oerp.login(USER, PASSWD)
        # Check the type of the result returned
        result = oerp.search('res.users', [])
        self.assertEqual(type(result), type([]))

