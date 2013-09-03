# -*- coding: utf-8 -*-
"""Provide the :class:`Inspect` class which can output useful data
from `OpenERP`.
"""
from functools import wraps

from oerplib import error


def check_pydot(func):
    @wraps(func)
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

    .. automethod:: relations(models, maxdepth=1, whitelist=[], blacklist=[], attrs_whitelist=[], attrs_blacklist=[], config={})

        Return a :class:`Relations <oerplib.service.inspect.relations.Relations>`
        object showing relations between data models, starting from `models`
        (depth = 0) and iterate recursively until reaching the `maxdepth` limit.

        `whitelist` and `blacklist` of models can be defined with patterns
        (a joker ``*`` can be used to match several models like ``account*``).
        The whitelist has a lower priority than the blacklist, and all models
        declared in `models` are automatically integrated to the `whitelist`.

        In the same way, displaying attributes can be defined for each model
        with ``attrs_whitelist`` and ``attrs_blacklist``. By default, model
        attributes are not displayed, unless the ``'*'`` pattern is supplied in
        ``attrs_whitelist``, or if only the ``attrs_blacklist`` if defined.

            >>> oerp.inspect.relations(
            ...     ['res.users'],
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
            - ``color_function: #D9602E``
            - ``space_between_models: 0.25``,

        >>> oerp.inspect.relations(
        ...     ['res.users'],
        ...     config={'relation_types': ['many2one']}
        ... ).write('res_users.png', format='png')

        .. note::
            With `OpenERP` < `6.1`, `many2one` and `one2many` relationships can
            not be bound together. Hence, a `one2many` relationship based on a
            `many2one` will draw a separate arrow.

    """
    def __init__(self, oerp):
        self._oerp = oerp

    @check_pydot
    def relations(self, models, maxdepth=1, whitelist=None, blacklist=None,
                  attrs_whitelist=None, attrs_blacklist=None, config=None):
        from oerplib.service.inspect.relations import Relations
        return Relations(
            self._oerp, models, maxdepth, whitelist, blacklist,
            attrs_whitelist, attrs_blacklist, config)

    def scan_on_change(self, models):
        """Scan all `on_change` methods detected among views of `models`, and
        returns a dictionary formatted as
        ``{model: {on_change: {view_name: field: [args]}}}``

            >>> oerp.inspect.scan_on_change(['sale.order'])
            {'sale.order': {
                'onchange_partner_id': {
                    'sale.view_order_form': {
                        'partner_id': ['partner_id']}},
                'onchange_partner_order_id': {
                    'sale.view_order_form': {
                        'partner_order_id': ['partner_order_id', 'partner_invoice_id', 'partner_shipping_id']}},
                'onchange_pricelist_id': {
                    'sale.view_order_form': {
                        'pricelist_id': ['pricelist_id', 'order_line']}},
                'onchange_shop_id': {
                    'sale.view_order_form': {
                        'shop_id': ['shop_id']}},
                'shipping_policy_change': {
                    'sale.view_order_form': {
                        'order_policy': ['order_policy']}}},
             'sale.order.line': {
                'product_id_change': {
                    'sale.view_order_form': {
                        'product_id': [
                            'parent.pricelist_id', 'product_id', 'product_uom_qty', 'product_uom',
                            'product_uos_qty', 'product_uos', 'name', 'parent.partner_id', False, True,
                            'parent.date_order', 'product_packaging', 'parent.fiscal_position', False, 'context'],
                        'product_uom_qty': [
                            'parent.pricelist_id', 'product_id', 'product_uom_qty', 'product_uom',
                            'product_uos_qty', 'product_uos', 'name', 'parent.partner_id', False, False,
                            'parent.date_order', 'product_packaging', 'parent.fiscal_position', True, 'context']}},
                ...
             }}
        """
        from oerplib.service.inspect.on_change import scan_on_change
        return scan_on_change(self._oerp, models)

    def modules(self, models=None, models_blacklist=None,
                restrict=False, config=None):
        """Return a :class:`Modules <oerplib.service.inspect.modules.Modules>`
        object describing dependencies between modules related to the list of
        `models`.

        `models` and `models_blacklist` parameters can be defined with patterns
        (a joker ``*`` can be used to match several models like ``account*``).
        The whitelist (`models`) has a lower priority than the blacklist
        (`models_blacklist`).

            >>> oerp.inspect.modules(
            ...     ['res.partner*'],
            ...     ['res.partner.title', 'res.partner.bank'],
            ... ).write('modules_res_partner.png', format='png')

        TODO: restrict parameter

        `config` is a dictionary of options to override some attributes of
        the graph. Here the list of options and their default values:

            - ``bgcolor_module_title: #DEDFDE``,
            - ``color_module_title: black``,
            - ``bgcolor_module_title_root: #A50018``,
            - ``color_module_title_root: white``,
            - ``bgcolor_module_title_highlight: #1F931F``,
            - ``color_module_title_highlight: white``,
            - ``bgcolor_module: white``,
            - ``color_model: black``,
            - ``color_comment: grey``,
            - ``show_transient_models: False``,

        .. note::
            With `OpenERP` `5.0`, data models can not be bound to their related
            modules, and as such the `models` and `models_blacklist`
            parameters are ignored.

        """
        from oerplib.service.inspect.modules import Modules
        return Modules(
            self._oerp, models, models_blacklist, restrict, config)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
