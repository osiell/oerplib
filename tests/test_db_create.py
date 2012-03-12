# -*- coding: UTF-8 -*-

import unittest

import oerplib
from oerplib.service import osv


#TODO: delete later
SERVER = '192.168.1.10'
PROTOCOL = 'xmlrpc'
PORT = 8069
USER = 'admin'
PASSWD = 'admin'
DATABASE = 'oerplib-test'


class TestDB(unittest.TestCase):

    def setUp(self):
        #TODO: get parameters in a configuration file or command line
        pass

    def test_db_list(self):
        pass

    def test_db_list_lang(self):
        pass

    def test_db_create(self):
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
