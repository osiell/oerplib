# -*- coding: UTF-8 -*-

import unittest
import datetime

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
            False)  # Wrong arg

    def test_write_record_char(self):
        backup_name = self.user.name
        self.user.name = "Charly"
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.name, "Charly")
        self.user.name = backup_name
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.name, backup_name)

    def test_write_record_boolean(self):
        self.user.active = False
        self.user.active = True
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.active, True)

    def test_write_record_float(self):
        partner = self.user.company_id.partner_id
        partner.credit_limit = False
        self.oerp.write_record(partner)
        self.assertEqual(partner.credit_limit, 0.0)
        partner.credit_limit = 0.0
        self.oerp.write_record(partner)
        self.assertEqual(partner.credit_limit, 0.0)

    def test_write_record_integer(self):
        cur = self.oerp.browse('res.currency', 1)
        backup_accuracy = cur.accuracy
        cur.accuracy = False
        self.oerp.write_record(cur)
        self.assertEqual(cur.accuracy, 0)
        cur.accuracy = backup_accuracy
        self.oerp.write_record(cur)
        self.assertEqual(cur.accuracy, backup_accuracy)

    def test_write_record_selection(self):
        self.user.context_tz = False
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.context_tz, False)
        self.user.context_tz = 'Europe/Paris'
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.context_tz, 'Europe/Paris')

    def test_write_record_date(self):
        partner = self.user.company_id.partner_id
        partner.date = False
        self.oerp.write_record(partner)
        self.assertEqual(partner.date, False)
        partner.date = '2012-01-01'
        self.oerp.write_record(partner)
        self.assertEqual(partner.date, datetime.date(2012, 1, 1))
        partner.date = datetime.date(2012, 1, 1)
        self.oerp.write_record(partner)
        self.assertEqual(partner.date, datetime.date(2012, 1, 1))

    def test_write_record_datetime(self):
        version = self.oerp.db.server_version()
        # OpenERP 5.0.X
        if version[:3] in ['5.0']:
            act = self.oerp.browse('ir.actions.todo', 1)
            act.start_date = False
            self.oerp.write_record(act)
            self.assertEqual(act.start_date, False)
            act.start_date = '2012-01-01 0:0:0'
            self.oerp.write_record(act)
            self.assertEqual(act.start_date, datetime.datetime(2012, 1, 1))
            act.start_date = datetime.datetime(2012, 1, 1)
            self.oerp.write_record(act)
            self.assertEqual(act.start_date, datetime.datetime(2012, 1, 1))
        # OpenERP 6.0.X
        elif version[:3] in ['6.0']:
            # TODO
            pass

    def test_write_record_many2one(self):
        backup_company = self.user.company_id
        self.user.company_id = False
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.company_id, False)
        self.user.company_id = backup_company
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.company_id.id, backup_company.id)
        self.user.company_id = backup_company.id
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.company_id.id, backup_company.id)

    def test_write_record_many2many(self):
        backup_groups = [grp for grp in self.user.groups_id]
        # False
        self.user.groups_id = False
        self.oerp.write_record(self.user)
        self.assertEqual(list(self.user.groups_id), backup_groups)
        # []
        self.user.groups_id = []
        self.oerp.write_record(self.user)
        self.assertEqual(list(self.user.groups_id), backup_groups)
        # [(6, 0, ...)]
        self.user.groups_id = [(6, 0, [grp.id for grp in backup_groups])]
        self.oerp.write_record(self.user)
        self.assertEqual(list(self.user.groups_id), backup_groups)

    def test_write_record_one2many(self):
        partner = self.user.company_id.partner_id
        backup_address = [addr for addr in partner.address]
        # False
        partner.address = False
        self.oerp.write_record(partner)
        self.assertEqual(list(partner.address), backup_address)
        # []
        partner.address = []
        self.oerp.write_record(partner)
        self.assertEqual(list(partner.address), backup_address)
        # [(1, ID, { values })]
        addr_id = list(partner.address)[0].id
        partner.address = [(1, addr_id, {'name': u"OERPLib-test"})]
        self.oerp.write_record(partner)
        self.assertEqual(list(partner.address), backup_address)
        addr = list(partner.address)[0]
        self.assertEqual(addr.name, u"OERPLib-test")

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
