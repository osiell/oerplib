# -*- coding: utf-8 -*-
"""Provide the :class:`Inspect` class which can output useful data
from `OpenERP`.
"""

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
    >>> user = oerp.login('admin', 'passwd', 'database')
    >>> oerp.inspect
    <oerplib.service.inspect.Inspect object at 0xb42fa84f>

    .. automethod:: relations(model, maxdepth=1, whitelist=[], blacklist=[], attrs_whitelist=[], attrs_blacklist=[], config={})

        Return a :class:`Relations <oerplib.service.inspect.relations.Relations>`
        object showing relations between data models, starting from `model`
        (depth = 0) and iterate recursively until reaching the `maxdepth` limit.

        `whitelist` and `blacklist` of models can be defined with patterns
        (a joker ``*`` can be used to match several models like ``account*``),
        the whitelist is processed before the blacklist.

        In the same way, displaying attributes can be defined for each model
        with ``attrs_whitelist`` and ``attrs_blacklist``. By default, model
        attributes are not displayed, unless the ``'*'`` pattern is supplied in
        ``attrs_whitelist``, or if only the ``attrs_blacklist`` if defined.

            >>> oerp.inspect.relations(
            ...     'res.users',
            ...     maxdepth=4,
            ...     whitelist=['res*'],
            ...     blacklist=['res.users'],
            ...     attrs_whitelist=['*'],
            ...     attrs_blacklist=['res.partner', 'res.company'],
            ... ).write('res_users.png', format='png')

        `config` is a dictionary of options to override some attributes of
        the graph. Here the list of options and their default values:

            - ``relation_types: ['many2one', 'one2many', 'many2many']``,
            - ``show_many2many_table: False``,
            - ``color_many2one: #0E2548``,
            - ``color_one2many: #008200``,
            - ``color_many2many: #6E0004``,
            - ``bgcolor_model_title: #64629C``,
            - ``color_model_title: white``,
            - ``color_model_subtitle': #3E3D60``,
            - ``bgcolor_model: white``,
            - ``color_normal: black``,
            - ``color_required: blue``
            - ``space_between_models: 0.25``,

        >>> oerp.inspect.relations(
        ...     'res.users',
        ...     config={'relation_types': ['many2one']}
        ... ).write('res_users.png', format='png')

        .. note::
            With `OpenERP` < `6.0`, `many2one` and `one2many` relationships can
            not be bound together. Hence, a `one2many` relationship based on a
            `many2one` will draw a separate arrow.

    """
    def __init__(self, oerp):
        self._oerp = oerp

    @check_pydot
    def relations(self, model, maxdepth=1, whitelist=None, blacklist=None,
                  attrs_whitelist=None, attrs_blacklist=None, config=None):
        from oerplib.service.inspect.relations import Relations
        return Relations(
            self._oerp, model, maxdepth, whitelist, blacklist,
            attrs_whitelist, attrs_blacklist, config)

    def scan_on_change(self, models):
        """List all `on_change` methods detected among `models`.
        The detection is made from the view descriptions related to the models.
        """
        from oerplib.service.inspect.on_change import scan_on_change
        return scan_on_change(self._oerp, models)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
