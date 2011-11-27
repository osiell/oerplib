# -*- coding: UTF-8 -*-
"""This module contains the OERP class which manage the interaction with
the OpenERP server.
"""
import os
import collections
import base64, zlib, tempfile

from oerplib import connector, error, osv, pool

class OERP(collections.MutableMapping):
    """Return a new instance of the :class:`OERP` class.
    The optional ``database`` parameter specifies the default database to use
    when the ``login(user, passwd)`` is called. By default, the port 8069
    is used.

    """
#    Attributes:
#    user        -- object which contains User's informations
#    server      -- domain name or IP of the server
#    port        -- port used to connect to the server
#    database    -- database name


    def __init__(self, server, database=None, port=8069, protocol='xmlrpc'):
        self.server = server
        self.port = port
        self.protocol = protocol
        self.database = self.database_default = database
        self.pool = pool.OSVPool(self)
        #NOTE: create a fake User object just to execute the
        # first query : browse the real User object
        self.user = type('User', (object,), {
                            'id': None,
                            'login': None,
                            'password': None,
                        })

    def login(self, user, passwd, database=None):
        """Log in as the given ``user`` with the password ``passwd`` on the
        database ``database`` and return the corresponding User browsable
        object.
        If ``database`` is not specified, the default one will be used instead.
        If no database is found, a LoginError exception will be raised.

        """
        # Raise an error if no database was given
        self.database = database or self.database_default
        if not self.database:
            raise error.LoginError(u"No database specified")
        # Instanciate the OpenERP server connector
        self.connector = connector.get_connector(self.server, self.port,
                                                 self.protocol)
        # Get the user's ID and generate the corresponding User object
        try:
            user_id = self.connector.login(self.database, user, passwd)
        except connector.LoginError as exc:
            raise error.LoginError(unicode(exc))
        else:
            if user_id:
                self.user.id = user_id
                self.user.login = user
                self.user.password = passwd
                self.user = self.browse('res.users', user_id)
                return self.user
            else:
                raise error.LoginError(u"Wrong login ID or password")

    # ------------------------- #
    # -- Raw XML-RPC methods -- #
    # ------------------------- #

    def execute(self, osv_name, method, *args, **kwargs):
        """Execute a simple XMLRPC method ``method`` on the OSV server class
        ``osv_name``. ``*args`` parameters varies according to the method used.

        """
        # Raise an error if no user is logged
        if not self.user:
            raise error.LoginError(
                u"Have to be logged to be able to execute queries")
        # Execute the query
        try:
            return self.connector.execute(self.user.id, self.user.password,
                                          osv_name, method, *args, **kwargs)
        except connector.ExecuteError as exc:
            raise error.ExecuteQueryError(unicode(exc))

    def exec_workflow(self, osv_name, signal, obj_id):
        """XMLRPC Workflow query. Execute the workflow signal ``signal`` on
        the instance having the ID ``obj_id`` of OSV server class ``osv_name``.

        `WARNING: not sufficiently tested.`

        """
        # Raise an error if no user is logged
        if not self.user:
            raise error.LoginError(
                u"Have to be logged to be able to execute queries")
        # Execute the workflow query
        try:
            self.connector.exec_workflow(self.user.id, self.user.password,
                                         osv_name, signal, obj_id)
        except connector.ExecWorkflowError as exc:
            raise error.WorkflowQueryError(unicode(exc))

    def report(self, report_name, osv_name, obj_id, report_type='pdf',
               context=None):
        """Download a report from the OpenERP server via XMLRPC
        and return the path of the file.
        ``report_type`` can be 'pdf', 'webkit', etc.

        """
        if context is None:
            context = {}
        # Raise an error if no user is logged
        if not self.user:
            raise error.LoginError(
                u"Have to be logged to be able to execute queries")
        # Set the language of the user connected as the
        # context language by default
        if 'lang' not in context:
            context['lang'] = self.user.context_lang
        # Execute the report query
        try:
            pdf_data = self.connector.report(self.user.id, self.user.password,
                                             report_name, osv_name,
                                             obj_id, report_type, context)
        except connector.ExecReportError as exc:
            raise error.ReportError(unicode(exc))
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
            return self.pool.get(osv_name).browse(ids, refresh)

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

    def read(self, osv_name, ids, fields=None):
        """Return the ID of each record with the values
        of the requested fields ``fields`` from the OSV server class
        ``osv_name``. If ``fields`` is not specified, all fields values
        will be retrieved.

        """
        if fields is None:
            fields = []
        return self.execute(osv_name, 'read', ids, fields)

    def write(self, osv_obj, ids=None, vals=None):
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
        if ids is None:
            ids = []
        if vals is None:
            vals = {}
        if isinstance(osv_obj, osv.OSV):
            return self.pool.get_by_class(osv_obj.__class__).write(osv_obj)
        return self.execute(osv_obj, 'write', ids, vals)

    def unlink(self, osv_obj, ids=None):
        """Delete records with the given IDs (e.g. ``[1, 42, ...]``).
        ``osv`` parameter may be the OSV server class name
        (e.g. ``'sale.order'``) or an OSV instance (browsable object).
        In the latter case, the parameter ``ids`` is useless.
        Return True.

        """
        if ids is None:
            ids = []
        if isinstance(osv_obj, osv.OSV):
            return self.pool.get(osv_obj.__osv__['name']).unlink(osv_obj)
        return self.execute(osv_obj, 'unlink', ids)

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
        if not isinstance(osv_obj, osv.OSV):
            raise ValueError(u"Value is not an instance of OSV class")
        return osv_obj.__osv__['name']
        #return self.pool.get_by_class(osv_obj.__class__).osv['name']

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
