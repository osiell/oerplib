# -*- coding: utf-8 -*-
"""Provide the :class:`Inspect` class which can output useful data
from `OpenERP`.
"""

from oerplib import error
from oerplib.tools import v


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
    >>> user = oerp.login('admin', 'passwd', 'database')
    >>> oerp.inspect
    <oerplib.service.inspect.Inspect object at 0xb42fa84f>

    .. automethod:: relations(model, maxdepth=1, blacklist=[], whitelist=[], config={})

        Return a :class:`Relations <oerplib.service.inspect.relations.Relations>`
        object showing relations between data models, starting from `model`
        (depth = 0) and iterate recursively until reaching the `maxdepth` limit.
        `blacklist` and `whitelist` of models can be defined (a joker ``*`` can
        be used to match several models like ``account*``).

            >>> oerp.inspect.relations(
            ...     'res.users',
            ...     maxdepth=4,
            ...     blacklist=['ir*'],
            ...     rel_types=['many2one', 'many2many']
            ... ).write('res_users.png', format='png')

        `config` is a dictionary of options to override some attributes of
        the graph. Here the list of options and their default values:

            - ``relation_types: ['many2one', 'one2many', 'many2many']``,
            - ``show_model_attrs: True``,
            - ``show_many2many_table: False``,
            - ``color_many2one: #0E2548``,
            - ``color_one2many: #008200``,
            - ``color_many2many: #6E0004``,
            - ``bgcolor_model_title: #64629C``,
            - ``color_model_title: white``,
            - ``bgcolor_model: white``,
            - ``color_normal: black``,
            - ``color_required: blue``

        >>> oerp.inspect.relations(
        ...     'res.users',
        ...     config={'show_model_attrs': False}
        ... ).write('res_users.png', format='png')

        .. note::
            With `OpenERP` < `6.0`, `many2one` and `one2many` relationships can
            not be bound together. Hence, a `one2many` relationship based on a
            `many2one` will draw a separate arrow.

    """
    def __init__(self, oerp):
        self._oerp = oerp

    @check_pydot
    def relations(self, model, maxdepth=1, blacklist=None, whitelist=None,
                  config=None):
        from oerplib.service.inspect.relations import Relations
        return Relations(
            self._oerp, model, maxdepth, blacklist, whitelist, config)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
