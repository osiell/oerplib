# -*- coding: UTF-8 -*-
"""This module contains the OERP class which manage the interaction with
the OpenERP server.
"""
import xmlrpclib, socket
import os
import time
import collections
import traceback, sys
import base64, zlib, tempfile

from oerplib import error
from oerplib import factory
from oerplib import pool

class OERP(collections.MutableMapping):
    """Return a new instance of the :class:`OERP` class.
    The optional *database* parameter specifies the default database to use
    when the ``login(user, passwd)`` is called. By default, the port 8069
    is used.

    """
#    Attributes:
#    user        -- object which contains User's informations
#    server      -- domain name or IP of the server
#    port        -- port used to connect to the server
#    database    -- database name


    def __init__(self, server, database=None, port=8069):
        self.server = server
        self.port = port
        self.database = self.database_default = database
        self.pool = pool.OSVPool(self)
        self.user = False
        self.xmlrpc_url = 'http://{server}:{port}/xmlrpc'.format(
                server=self.server,
                port=self.port)
        self.sock = xmlrpclib.ServerProxy(self.xmlrpc_url+'/object')
        self.sock_report = xmlrpclib.ServerProxy(self.xmlrpc_url+'/report')
        self.sock_common = xmlrpclib.ServerProxy(self.xmlrpc_url+'/common')

    def login(self, user, passwd, database=None):
        """Log in as the given ``user`` with the password ``passwd`` on the
        database ``database`` and return the corresponding User browsable
        object.
        If ``database`` is not specified, the default one will be used instead.
        If no database is found, a LoginError exception will be raised.

        """
        self.database = database or self.database_default
        if not self.database:
            raise error.LoginError(u"No database specified")
        try:
            user_id = self.sock_common.login(self.database, user, passwd)
        except xmlrpclib.Fault as exc:
            #NOTE: exc.faultCode is in unicode
            raise error.LoginError(u"{0}".format(repr(exc.faultCode)))
        except socket.error as exc:
            raise error.LoginError(u"{0}".format(exc.strerror))
        else:
            if user_id:
                #NOTE: create a fake User object just to execute the
                # first query : browse the real User object
                self.user = type('User', (object,), {
                                    'id': user_id,
                                    'login': user,
                                    'password': passwd,
                                })
                self.user = self.browse('res.users', user_id)
                return self.user
            else:
                raise error.LoginError(u"Wrong login ID or password")

    # ------------------------- #
    # -- Raw XML-RPC methods -- #
    # ------------------------- #

    def execute(self, osv_name, method, *args):
        """Execute a simple XMLRPC method ``method`` on the OSV server class
        ``osv_name``. ``*args`` parameters varies according to the method used.

        """
        if not self.user:
            raise error.LoginError(
                u"Have to be logged to be able to execute queries")
        try:
            return self.sock.execute(
                        self.database, self.user.id,
                        self.user.password, osv_name, method, *args)
        except xmlrpclib.Error as exc:
            raise error.ExecuteQueryError(u"{0}".format(exc.faultCode
                                                        or "Unknown error"),
                                          exc.faultString)

    def exec_workflow(self, *args):
        """XMLRPC Workflow query.

        `WARNING: not sufficiently tested.`

        """
        if not self.user:
            raise error.LoginError(
                u"Have to be logged to be able to execute queries")
        #TODO need to be tested + fix exception
        try:
            return self.sock.exec_workflow(
                        self.database, self.user.id,
                        self.user.password, *args)
        except Exception as exc:
            raise error.WorkflowQueryError(
                        u"Workflow query has failed")

    def exec_report(self, report_name, osv_name, obj_id, report_type='pdf'):
        """Download a report from the OpenERP server via XMLRPC
        and return the path of the file.

        `WARNING: not sufficiently tested.`

        """
        if not self.user:
            raise error.LoginError(
                u"Have to be logged to be able to execute queries")
        data = {'model': osv_name, 'id': obj_id, 'report_type': report_type}
        try:
            report_id = self.sock_report.report(self.database, self.user.id,
                    self.user.password, report_name, [obj_id], data)
        except xmlrpclib.Error as exc:
            raise error.ReportError(u"{0}".format(exc.faultCode))
        state = False
        attempt = 0
        while not state:
            try:
                pdf_data = self.sock_report.report_get(self.database,
                        self.user.id, self.user.password, report_id)
            except xmlrpclib.Error as exc:
                raise error.ReportError(u"{0}".format(exc.faultString))
            state = pdf_data['state']
            if not state:
                time.sleep(1)
                attempt += 1
            if attempt > 200:
                raise error.ReportError(u"Download time exceeded, " + \
                                        u"the operation has been canceled.")
        return self.__print_file_data(pdf_data)

    @staticmethod
    def __print_file_data(data):
        """Print data in a temporary file and return the path of this one."""
        if 'result' not in data:
            raise error.ReportError(
                    u"Invalid data, the operation has been canceled.")
        content = base64.decodestring(data['result'])
        if data.get('code') == 'zlib':
            content = zlib.decompress(content)

        if data['format'] in ['pdf', 'html', 'doc', 'xls',
                              'sxw', 'odt', 'tiff']:
            if data['format'] == 'html' and os.name == 'nt':
                data['format'] = 'doc'
            (file_no, file_path) = tempfile.mkstemp('.'+data['format'],
                                                    'oerplib_')
            with file(file_path, 'wb+') as fp:
                fp.write(content)
            os.close(file_no)
            return file_path

    # ------------------------- #
    # -- High Level methods  -- #
    # ------------------------- #

    def browse(self, osv_name, ids, refresh=True):
        """Return a browsable object (or a list of objects)
        according to the OSV name and ID (or IDs) supplied.
        ``refresh`` option will reinitialize the object if this one has
        already been loaded previously (this is the default behaviour, set to
        False to change that).

        """
        if isinstance(ids, list):
            return [self.browse(osv_name, o_id, refresh)
                    for o_id in ids]
        else:
            return self.pool.get(osv_name).generate_browse_record(ids, refresh)

    def search(self, osv_name, args):
        """Return a list of IDs of records matching the given criteria in
        ``args`` parameter. ``args`` must be of the form
        ``[('name', '=', 'John'), (...)]``

        """
        return self.execute(osv_name, 'search', args)

    def create(self, osv_name, vals):
        """Create a new record with the specified values contained in the
        ``vals`` dictionary (e.g. ``{'name': 'John', ...}``).
        Return the ID of the new record.

        """
        return self.execute(osv_name, 'create', vals)

    def read(self, osv_name, ids, fields=[]):
        """Return the ID of each record with the values
        of the requested fields ``fields`` from the OSV server class
        ``osv_name``. If ``fields`` is not specified, all fields values
        will be retrieved.

        """
        return self.execute(osv_name, 'read', ids, fields)

    def write(self, osv, ids=[], vals={}):
        """Update records with given IDs (e.g. ``[1, 42, ...]``)
        with the given values contained in the ``vals`` dictionary
        (e.g. ``{'name': 'John', ...}``).
        ``osv`` parameter may be the OSV server class name
        (e.g. ``'sale.order'``) or an ``OSV`` instance (browsable object).
        In the latter case, ``vals`` will automatically contain all the changed
        values of the object and ``ids`` the object ID, thus the parameters
        ``ids`` and ``vals`` are useless.
        Return True.

        """
        if isinstance(osv, factory.OSV):
            return self.pool.get_by_class(osv.__class__).write(osv)
        return self.execute(osv, 'write', ids, vals)

    def unlink(self, osv, ids=[]):
        """Delete records with the given IDs (e.g. ``[1, 42, ...]``).
        ``osv`` parameter may be the OSV server class name
        (e.g. ``'sale.order'``) or an OSV instance (browsable object).
        In the latter case, the parameter ``ids`` is useless.
        Return True.

        """
        if isinstance(osv, factory.OSV):
            return self.pool.get_by_class(osv.__class__).unlink(osv)
        return self.execute(osv, 'unlink', ids)

    def refresh(self, osv_obj):
        """Restore original values of the object ``osv_obj`` from data
        retrieved on the OpenERP server.
        Thus, all changes made locally on the object are canceled.

        """
        return self.pool.get_by_class(osv_obj.__class__).refresh(osv_obj)

    def reset(self, osv_obj):
        """Cancel all changes made locally on the object ``osv_obj``.
        No request to the server is executed to perform this operation.
        Therefore, values restored may be outdated.

        """
        return self.pool.get_by_class(osv_obj.__class__).reset(osv_obj)

    def get_osv_name(self, osv_obj):
        """Return the OSV name of the OSV instance ``osv_obj`` supplied."""
        if not isinstance(osv_obj, factory.OSV):
            raise ValueError(u"Value is not an instance of OSV class")
        return self.pool.get_by_class(osv_obj.__class__).osv['name']

    def __str__(self):
        return str(self.pool)

    # ---------------------------- #
    # -- MutableMapping methods -- #
    # ---------------------------- #

    def __delitem__(self, osv_name):
        del self.pool[osv_name]
        #raise error.NotAllowedError(u"Operation not supported")

    def __getitem__(self, osv_name):
        return self.pool[osv_name]

    def __iter__(self):
        for osv_name in self.pool:
            yield osv_name

    def __len__(self):
        return len(self.pool)

    def __setitem__(self, osv_name, value):
        raise error.NotAllowedError(u"Operation not supported")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
