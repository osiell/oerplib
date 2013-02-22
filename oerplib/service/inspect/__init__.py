# -*- coding: utf-8 -*-
"""Provide the :class:`Inspect` which can output useful data from `OpenERP`."""

from oerplib import error


def check_pydot(func):
    def wrapper(*args, **kwargs):
        try:
            import pydot
        except:
            raise error.InternalError(
                "'pydot' module not found")
        else:
            return func(*args, **kwargs)
    return wrapper


class Inspect(object):
    """.. versionadded:: 0.8

    The `Inspect` class provides methods to output useful data from `OpenERP`.

    .. note::
        This service have to be used through the :attr:`oerplib.OERP.inspect`
        property.

    >>> import oerplib
    >>> oerp = oerplib.OERP('localhost')
    >>> oerp.inspect
    <oerplib.service.inspect.Inspect object at 0xb42fa84f>

    """
    def __init__(self, oerp):
        self._oerp = oerp

    @check_pydot
    def relations(self, model, maxdepth=1, blacklist=None):
        """TODO"""
        from oerplib.service.inspect.relations import Relations
        return Relations(self._oerp, model, maxdepth, blacklist)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
