# -*- coding: UTF-8 -*-
"""Provide the :class:`DB` class in order to manage the `OpenERP` databases."""

import time

from oerplib import rpc, error


class DB(object):
    """.. versionadded:: 0.4.0

    The `DB` class represents the database management service.
    It provides functionalities such as list, create, drop, dump
    and restore databases.

    .. note::
        This service have to be used through the :attr:`oerplib.OERP.db`
        property.

    >>> import oerplib
    >>> oerp = oerplib.OERP('localhost')
    >>> oerp.db
    <oerplib.service.db.DB object at 0xb75fb04c>

    .. warning::

        All methods documented below are not strictly implemented in `OERPLib`
        (except the
        :func:`create_and_wait <oerplib.service.db.DB.create_and_wait>` method).

        Method calls are purely dynamic, and the following documentation can be
        wrong if the API of `OpenERP` is changed between versions. Anyway, if
        you known the API used by the `OpenERP` server for the ``/db`` RPC
        service, it will work.

    .. method:: DB.list()

        Return a list of the `OpenERP` databases:

        >>> oerp.db.list()
        >>> ['production_db', 'test_db']

        :return: a list of database names

    .. method:: DB.list_lang()

        Return a list of codes and names of language supported by `OpenERP`:

        >>> oerp.db.list_lang()
        >>> [['sq_AL', u'Albanian / Shqipëri'], ['ar_AR', 'Arabic / الْعَرَبيّة'], ...]

        :return: a list of pairs representing languages with their codes and
                 names

    .. method:: DB.server_version()

        Return the version of the `OpenERP Server`:

        >>> oerp.db.server_version()
        >>> '6.1'

        :return: the version of the `OpenERP Server` as string

    .. method:: DB.dump(super_admin_passwd, database)

        Return a dump of `database` in `base64`:

        >>> binary_data = oerp.db.dump('super_admin_passwd', 'production_db')

        The super administrator password `super_admin_passwd` of `OpenERP` is
        required to perform this action.

        :return: the `base64` string representation of the `database`

    .. method:: DB.restore(super_admin_passwd, database, binary_data)

        Restore in `database` a dump previously created with the
        :func:`dump <DB.dump>` method:

        >>> oerp.db.restore('super_admin_passwd', 'test_db', binary_data)

        The super administrator password `super_admin_passwd` of `OpenERP` is
        required to perform this action.

    .. method:: DB.drop(super_admin_passwd, database)

        Drop the `database` from `OpenERP`:

        >>> oerp.db.drop('super_admin_passwd', 'test_db')
        True

        The super administrator password `super_admin_passwd` of `OpenERP` is
        required to perform this action.

        :return: True

    .. method:: DB.create(super_admin_passwd, database, demo_data=False, lang='en_US', admin_passwd='admin')

        Request the `OpenERP` server to create a new database named `database`
        which will have `admin_passwd` as administrator password and localized
        with the `lang` parameter.
        You have to set the flag `demo_data` to `True` in order to insert
        demonstration data.

        As the creating process may take some time, you can execute the
        :func:`get_process <DB.get_process>` method with the database ID
        returned to know its current state.

        >>> database_id = oerp.db.create('super_admin_passwd', 'test_db', False, 'fr_FR', 'my_admin_passwd')

        The super administrator password `super_admin_passwd` of `OpenERP` is
        required to perform this action.

        :return: the ID of the new database

    .. method:: DB.get_process(super_admin_passwd, database_id)

        Check the state of the creating process for the database identified by
        the `database_id` parameter.

        >>> oerp.db.get_process('super_admin_passwd', database_id) # Just after the call to the 'create' method
        (0, [])
        >>> oerp.db.get_process('super_admin_passwd', database_id) # Once the database is fully created
        (1.0, [{'login': u'admin', 'password': u'admin', 'name': u'Administrator'},
               {'login': u'demo', 'password': u'demo', 'name': u'Demo User'}])

        :return: A tuple with the progressing state and a list
                of user accounts created (once the database is fully created).

    """
    def __init__(self, oerp):
        self._oerp = oerp

    def create_and_wait(self, super_admin_passwd, database, demo_data=False,
                        lang='en_US', admin_passwd='admin'):
        """
        .. note::

            This method is not part of the official API of `OpenERP`. It's just
            a wrapper around the :func:`create <DB.create>` and
            :func:`get_process <DB.get_process>` methods.

        Like the :func:`create <DB.create>` method, but waits the end of
        the creating process by executing the
        :func:`get_process <DB.get_process>` method regularly to check its
        state.

        >>> oerp.db.create_and_wait('super_admin_passwd', 'test_db', False, 'fr_FR', 'my_admin_passwd')
        [{'login': u'admin', 'password': u'admin', 'name': u'Administrator'},
         {'login': u'demo', 'password': u'demo', 'name': u'Demo User'}]

        The super administrator password `super_admin_passwd` of `OpenERP` is
        required to perform this action.

        :return: a list of user accounts created
        :raise: :class:`oerplib.error.RPCError`

        """
        try:
            db_id = self._oerp._connector.db.create(
                    super_admin_passwd, database, demo_data, lang, admin_passwd)
            progress = 0.0
            attempt = 0
            while progress < 1.0:
                result = self._oerp._connector.db.get_progress(
                                super_admin_passwd, db_id)
                progress = result[0]
                if progress < 1.0:
                    time.sleep(1)
                    attempt += 1
                if attempt > 300:
                    raise error.RPCError(
                            "Too many attempts, the operation"
                            " has been canceled.")
            return result[1]

        except rpc.error.ConnectorError as exc:
            #FIXME handle the exception with the UnicodeEncodeError for
            # the error 'the database already exists'.
            #print dir(exc)
            raise error.RPCError(exc)

    def __getattr__(self, method):
        def rpc_method(*args):
            try:
                meth = getattr(self._oerp._connector.db, method, False)
                return meth(*args)
            except rpc.error.ConnectorError as exc:
                raise error.RPCError(exc)
        return rpc_method

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
