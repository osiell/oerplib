# -*- coding: UTF-8 -*-
"""This module contains the ``OERP`` class which manage the interaction with
the `OpenERP` server.

"""
import os
import base64, zlib, tempfile

from oerplib import connector, error, pool, browse

def context_auto(index):
    """Decorator function, generate automatically a default context
    parameter if this one is not supplied to the decorated function.
    """
    def wrapper(func):
        def wrapped(*args, **kwargs):
            if len(args) < (index + 1) and 'context' not in kwargs:
                kwargs['context'] = args[0].execute('res.users', 'context_get')
            return func(*args, **kwargs)
        return wrapped
    return wrapper

#FIXME: deprecated
#def check_logged_user(func):
#    """Decorator function which check that a user is logged.
#    Otherwise, an error is raised.
#    """
#    def wrapper(*args, **kwargs):
#        if not args[0]._user:
#            raise error.LoginError(
#                u"Have to be logged to be able to execute queries")
#        return func(*args, **kwargs)
#    return wrapper


class OERP(object):
    """Return a new instance of the :class:`OERP` class.
    The optional ``database`` parameter specifies the default database to use
    when the ``login(user, passwd)`` is called. By default, the port 8069
    is used.

    """

    def __init__(self, server, database=None, port=8069, protocol='xmlrpc'):
        self._server = server
        self._port = port
        self._protocol = protocol
        self._database = self._database_default = database
        self._pool = pool.OSVPool(self)
        self._user = None

    user = property(lambda self: self._user,
                    doc="Return the user object connected.")
    server = property(lambda self: self._server,
                      doc="Return the server name used.")
    port = property(lambda self: self._port,
                    doc="Return the port used.")
    protocol = property(lambda self: self._protocol,
                        doc="Return the protocol used.")

    #NOTE: in the past this function was implemented as a decorator for other
    # methods needed to be checked, but Sphinx documentation generator is not
    # able to auto-document decorated methods.
    def _check_logged_user(self):
        """Check if a user is logged. Otherwise, an error is raised."""
        if not self._user:
            raise error.LoginError(
                u"User login required.")

    def login(self, user, passwd, database=None):
        """Log in as the given ``user`` with the password ``passwd`` on the
        database ``database`` and return the corresponding User browsable
        object.
        If ``database`` is not specified, the default one will be used instead.
        If no database is found, a LoginError exception will be raised.

        :raise: :class:`oerplib.error.LoginError`

        """
        # Raise an error if no database was given
        self._database = database or self._database_default
        if not self._database:
            raise error.LoginError(u"No database specified")
        # Instanciate the OpenERP server connector
        self.connector = connector.get_connector(self._server, self._port,
                                                 self._protocol)
        # Get the user's ID and generate the corresponding User object
        try:
            user_id = self.connector.login(self._database, user, passwd)
        except connector.LoginError as exc:
            raise error.LoginError(unicode(exc))
        else:
            if user_id:
                #NOTE: create a fake User object just to execute the
                # first query : browse the real User object
                self._user = type('User', (object,), {
                                    'id': None,
                                    'login': None,
                                    'password': None,
                                })
                self._user.id = user_id
                self._user.login = user
                self._user.password = passwd
                self._user = self.browse('res.users', user_id)
                return self._user
            else:
                raise error.LoginError(u"Wrong login ID or password")

    # ------------------------- #
    # -- Raw XML-RPC methods -- #
    # ------------------------- #

    def execute(self, osv_name, method, *args):
        """Execute a simple `XML-RPC` method ``method`` on the OSV server class
        ``osv_name``. ``*args`` parameters varies according to the method used.

        :raise: :class:`oerplib.error.ExecuteQueryError`

        """
        self._check_logged_user()
        # Execute the query
        try:
            return self.connector.execute(self._user.id, self._user.password,
                                          osv_name, method, *args)
        except connector.ExecuteError as exc:
            raise error.ExecuteQueryError(unicode(exc))

    def exec_workflow(self, osv_name, signal, obj_id):
        """`XML-RPC` Workflow query. Execute the workflow signal ``signal`` on
        the instance having the ID ``obj_id`` of OSV server class ``osv_name``.

        :raise: :class:`oerplib.error.WorkflowQueryError`

        `WARNING: not sufficiently tested.`

        """
        self._check_logged_user()
        # Execute the workflow query
        try:
            self.connector.exec_workflow(self._user.id, self._user.password,
                                         osv_name, signal, obj_id)
        except connector.ExecWorkflowError as exc:
            raise error.WorkflowQueryError(unicode(exc))

    @context_auto(index=5)
    def report(self, report_name, osv_name, obj_id, report_type='pdf',
               context=None):
        """Download a report from the OpenERP server via `XML-RPC`
        and return the path of the file.

        :raise: :class:`oerplib.error.ReportError`

        """
        self._check_logged_user()
        #TODO report_type: what it means exactly?

        # If no context was supplied, get the default one FIXME
        #context = context or self.get_user_context()

        # Execute the report query
        try:
            pdf_data = self.connector.report(self._user.id, self._user.password,
                                             report_name, osv_name,
                                             obj_id, report_type, context)
        except connector.ExecReportError as exc:
            raise error.ReportError(unicode(exc))
        return self._print_file_data(pdf_data)

    @staticmethod
    def _print_file_data(data):
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

    #@context_auto(index=3)
    def browse(self, osv_name, ids, context=None, refresh=True):
        """Return a browsable object (or a list of objects)
        according to the OSV name and ID (or IDs) supplied.
        ``refresh`` option will reinitialize the object if this one has
        already been loaded previously (this is the default behaviour, set to
        False to change that).

        :raise: :class:`oerplib.error.ExecuteQueryError`

        """
        if isinstance(ids, list):
            return [self.browse(osv_name, o_id, refresh)
                    for o_id in ids]
        else:
            return self._pool.get(osv_name).browse(ids, refresh)

    #@context_auto(index=6)
    def search(self, osv_name, args=None, offset=0, limit=None, order=None,
               context=None, count=False):
        """Return a list of IDs of records matching the given criteria in
        ``args`` parameter. ``args`` must be of the form
        ``[('name', '=', 'John'), (...)]``

        :raise: :class:`oerplib.error.ExecuteQueryError`

        """
        if args is None:
            args = []
        return self.execute(osv_name, 'search', args, offset, limit, order,
                            context, count)

    #@context_auto(index=3)
    def create(self, osv_name, vals, context=None):
        """Create a new record with the specified values contained in the
        ``vals`` dictionary (e.g. ``{'name': 'John', ...}``).
        Return the ID of the new record.

        :raise: :class:`oerplib.error.ExecuteQueryError`

        """
        return self.execute(osv_name, 'create', vals, context)

    #@context_auto(index=4)
    def read(self, osv_name, ids, fields=None, context=None):
        """Return the ID of each record with the values
        of the requested fields ``fields`` from the OSV server class
        ``osv_name``. If ``fields`` is not specified, all fields values
        will be retrieved.

        :raise: :class:`oerplib.error.ExecuteQueryError`

        """
        if fields is None:
            fields = []
        return self.execute(osv_name, 'read', ids, fields, context)

    #@context_auto(index=4)
    def write(self, osv_obj, ids=None, vals=None, context=None):
        """Update records with given IDs (e.g. ``[1, 42, ...]``)
        with the given values contained in the ``vals`` dictionary
        (e.g. ``{'name': 'John', ...}``).
        ``osv`` parameter may be the OSV server class name
        (e.g. ``'sale.order'``) or an ``OSV`` instance (browsable object).
        In the latter case, ``vals`` will automatically contain all the changed
        values of the object and ``ids`` the object ID, thus the parameters
        ``ids`` and ``vals`` are useless.
        Return True.

        :raise: :class:`oerplib.error.ExecuteQueryError`

        """
        if ids is None:
            ids = []
        if vals is None:
            vals = {}
        if isinstance(osv_obj, browse.BrowseRecord):
            return self._pool.get_by_class(osv_obj.__class__).write(osv_obj)
        return self.execute(osv_obj, 'write', ids, vals, context)

    #@context_auto(index=3)
    def unlink(self, osv_obj, ids=None, context=None):
        """Delete records with the given IDs (e.g. ``[1, 42, ...]``).
        ``osv`` parameter may be the OSV server class name
        (e.g. ``'sale.order'``) or an OSV instance (browsable object).
        In the latter case, the parameter ``ids`` is useless.
        Return True.

        :raise: :class:`oerplib.error.ExecuteQueryError`

        """
        if ids is None:
            ids = []
        if isinstance(osv_obj, browse.BrowseRecord):
            return self._pool.get(osv_obj.__osv__['name']).unlink(osv_obj)
        return self.execute(osv_obj, 'unlink', ids, context)

    def refresh(self, osv_obj):
        """Restore original values of the object ``osv_obj`` from data
        retrieved on the OpenERP server.
        Thus, all changes made locally on the object are canceled.

        :raise: :class:`oerplib.error.ExecuteQueryError`

        """
        return self._pool.get_by_class(osv_obj.__class__).refresh(osv_obj)

    def reset(self, osv_obj):
        """Cancel all changes made locally on the object ``osv_obj``.
        No request to the server is executed to perform this operation.
        Therefore, values restored may be outdated.

        """
        return self._pool.get_by_class(osv_obj.__class__).reset(osv_obj)

    def get_osv_name(self, osv_obj):
        """Return the OSV name of the OSV instance ``osv_obj`` supplied."""
        if not isinstance(osv_obj, browse.BrowseRecord):
            raise ValueError(u"Value is not a browse record.")
        return osv_obj.__osv__['name']

    def get_user_context(self):
        """Generate a default user context parameter.

        :raise: :class:`oerplib.error.ExecuteQueryError`

        """
        return self.execute('res.users', 'context_get')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
