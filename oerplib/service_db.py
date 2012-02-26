# -*- coding: UTF-8 -*-
"""Provide the :class:`DB` class in order to manage the `OpenERP` databases."""

import time

from oerplib import rpc, error


class DB(object):
    #TODO: documentation
    """Database management service."""
    def __init__(self, oerp):
        self._oerp = oerp

    def create(self, super_admin_pwd, database,
               demo_data=False, lang='en_US', admin_pwd='admin'):
        try:
            db_id = self._oerp._connector.db.create(super_admin_pwd, database,
                                                    demo_data, lang, admin_pwd)
            progress = 0.0
            attempt = 0
            while progress < 1.0:
                result = self._oerp._connector.db.get_progress(super_admin_pwd,
                                                               db_id)
                progress = result[0]
                if progress < 1.0:
                    time.sleep(1)
                    attempt += 1
                if attempt > 200:
                    raise error.ExecuteQueryError("Time exceeded, the operation"
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
