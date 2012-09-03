# -*- coding: UTF-8 -*-
"""Provide the :class:`Wizard` class in order to access the old-style wizards.
"""

from oerplib import rpc, error


class Wizard(object):
    r""".. versionadded:: 0.6.0

    The `Wizard` class represents the ``/wizard`` RPC service which
    lets you access to the old-style wizards.

    .. note::
        This service have to be used through the :attr:`oerplib.OERP.wizard`
        property.

    >>> import oerplib
    >>> oerp = oerplib.OERP('localhost')
    >>> user = oerp.login('admin', 'passwd', 'database')
    >>> oerp.wizard
    <oerplib.service.wizard.Wizard object at 0xb76266ac>

    .. warning::

        All methods documented below are not strictly implemented in `OERPLib`

        Method calls are purely dynamic, and the following documentation can be
        wrong if the API of `OpenERP` is changed between versions. Anyway, if
        you known the API used by the `OpenERP` server for the ``/wizard`` RPC
        service, it will work.

    .. method:: Wizard.create(wiz_name, datas=None)

        >>> oerp.wizard.create('wiz_name')
        1

        :return: the wizard's instance ID

    .. method:: Wizard.execute(wiz_id, datas, action='init', context=None)

        >>> oerp.wizard.execute(1, {'one_field': u"Value"})

    """
    def __init__(self, oerp):
        self._oerp = oerp

    def __getattr__(self, method):
        def rpc_method(*args):
            try:
                meth = getattr(self._oerp._connector.wizard, method, False)
                return meth(self._oerp.database, self._oerp.user.id, *args)
            except rpc.error.ConnectorError as exc:
                raise error.RPCError(exc.message, exc.oerp_traceback)
        return rpc_method

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
