# -*- coding: UTF-8 -*-
"""Provide the :class:`DB` class in order to manage the `OpenERP` databases."""

import time

from oerplib import rpc, error


class DB(object):
    #TODO: documentation
    """The `DB` class represents the database management service.
    It provides functionalities such as list, create, drop, dump
    and restore databases.

    .. note::
        This service have to be used through the :attr:`OERP.db`
        property.

    >>> import oerplib
    >>> oerp = oerplib.OERP('localhost')
    >>> oerp.db
    <oerplib.service_db.DB object at 0xb75fb04c>

    .. method:: DB.list()

        Return a list of the `OpenERP` databases:

        >>> oerp.db.list()
        >>> ['production_db', 'test_db']

    .. method:: DB.list_lang()

        Return a list of codes and names of language supported by `OpenERP`:

        >>> oerp.db.list_lang()
        >>> [['sq_AL', u'Albanian / Shqipëri'], ['ar_AR', 'Arabic / الْعَرَبيّة'], ...]

    .. method:: DB.server_version()

        Return the version of the `OpenERP Server`:

        >>> oerp.db.server_version()
        >>> '6.1'

    .. method:: DB.dump(super_admin_passwd, database)

        Return a dump of `database` in `base64`:

        >>> binary_data = oerp.db.dump('super_admin_passwd', 'production_db')

        The super administrator password `super_admin_passwd` of `OpenERP` is
        required to perform this action.

    .. method:: DB.restore(super_admin_passwd, ...)

        TODO

        The super administrator password `super_admin_passwd` of `OpenERP` is
        required to perform this action.

    .. method:: DB.drop(admin_passwd, database)

        Drop the `database` from `OpenERP`:

        The super administrator password `super_admin_passwd` of `OpenERP` is
        required to perform this action.

        >>> oerp.db.drop('super_admin_passwd', 'test_db')
        True

    """
    def __init__(self, oerp):
        self._oerp = oerp

    def create(self, super_admin_passwd, database, demo_data=False,
               lang='en_US', admin_passwd='admin'):
        """Create a new database named `database` which will have `admin_passwd`
        as administrator password and localized with the `lang` parameter.
        You have to set the flag `demo_data` to `True` in order to insert
        demonstration data.

        The super administrator password `super_admin_passwd` of `OpenERP` is
        required to perform this action.

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
                    raise error.ExecuteQueryError(
                            "Too many attempts, the operation"
                            " has been canceled.")
            return result

        except rpc.error.ConnectorError as exc:
            #FIXME handle the exception with the UnicodeEncodeError for
            # the error 'the database already exists'.
            #print dir(exc)
            raise error.ExecuteQueryError(exc)

    def __getattr__(self, method):
        def rpc_method(*args):
            try:
                meth = getattr(self._oerp._connector.db, method, False)
                return meth(*args)
            except rpc.error.ConnectorError as exc:
                raise error.ExecuteQueryError(exc)
        return rpc_method

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
