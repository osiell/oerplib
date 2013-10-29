# -*- coding: utf-8 -*-
##############################################################################
#
#    OERPLib
#    Copyright (C) 2013 Sébastien Alix.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""Implements the :class:`Dependencies` class used to compute dependencies
between modules of an OpenERP server.
"""
import copy

from oerplib import error
from oerplib.tools import v

TPL_MODULE = """<
<table cellborder="0" cellpadding="0" cellspacing="0"
       border="1" bgcolor="{bgcolor_module}" height="100%%">
    <tr>
        <td border="0" bgcolor="{bgcolor_module_title}" align="center">
            <font color="{color_module_title}">{name}</font>
        </td>
    </tr>
    {models}
    {comment}
</table>>"""

TPL_MODULE_MODEL = """
<tr>
    <td align="left" border="0">- <font color="{color_model}">{model}</font></td>
</tr>
"""

TPL_MODULE_COMMENT = """
<tr>
    <td align="center" border="0"><font color="{color_comment}">{comment}</font></td>
</tr>
"""


def pattern2oerp(pattern):
    """Return a SQL expression corresponding to `pattern` (simpler
    representation of the SQL string matching).
    """
    return pattern.replace('*', '%')


class Dependencies(object):
    """Draw dependencies between modules. Models can be displayed in their
    respecting modules as well.
    """
    def __init__(self, oerp, modules=None, models=None, models_blacklist=None,
                 restrict=False, config=None):
        self._oerp = oerp
        self._restrict = restrict
        # Configuration options
        self._config = {
            'bgcolor_module_title': '#DEDFDE',
            'color_module_title': 'black',
            'bgcolor_module_title_root': '#A50018',
            'color_module_title_root': 'white',
            'bgcolor_module_title_highlight': '#1F931F',
            'color_module_title_highlight': 'white',
            'bgcolor_module': 'white',
            'color_model': 'black',
            'color_comment': 'grey',
            'show_normal_models': True,
            'show_transient_models': False,
        }
        self._config.update(config or {})
        # List of data models
        self._models = self._get_models_data(
            models or [], models_blacklist or [])
        # List of modules computed according to the `restrict` parameter
        # (display all modules or only modules related to data models)
        self._modules, self._modules_full = self._get_modules(
            self._restrict, self._models, keep=not bool(modules))
        # Fetch dependencies between modules
        self._scan_module_dependencies(modules or [])

    #@property
    #def models(self):
    #    """Returns a dictionary of all models used to draw the graph."""
    #    return self._models

    #@property
    #def modules(self):
    #    """Returns a dictionary of all modules used to draw the graph."""
    #    return self._modules

    def _get_models_data(self, models, models_blacklist):
        """Returns a dictionary `{MODEL: DATA, ...}` of models corresponding to
        `models - models_blacklist` patterns (whitelist substracted
        by a blacklist).
        """
        res = {}
        # OpenERP v5 does not have the 'modules' field on 'ir.model' used to
        # bound a data model and its related modules.
        if v(self._oerp._version) <= v('6.0'):
            return res
        models_patterns = \
            [pattern2oerp(model) for model in (models)]
        models_blacklist_patterns = \
            [pattern2oerp(model) for model in (models_blacklist)]
        if models:
            model_obj = self._oerp.get('ir.model')
            args = [('model', '=ilike', model)
                    for model in models_patterns]
            for _ in range(len(args) - 1):
                args.insert(0, '|')
            for model in models_blacklist_patterns:
                args.append('!')
                args.append(('model', '=ilike', model))
            ids = model_obj.search(args)
            for data in model_obj.read(ids, ['model', 'modules', 'osv_memory']):
                if not self._config['show_transient_models'] \
                        and data['osv_memory']:
                    continue
                if not self._config['show_normal_models'] \
                        and not data['osv_memory']:
                    continue
                res[data['model']] = {
                    'model': data['model'],
                    'modules': data['modules']
                    and data['modules'].split(', ') or [],
                }
        return res

    def _get_modules(self, restrict=False, models=None, keep=False):
        """Returns a dictionary `{MODULE: DATA, ...}` with all modules installed
        (`restrict=False`) or only with modules related to data models
        (`restrict=True`).
        """
        if models is None:
            models = {}
        modules = {}
        modules_full = {}
        # Fetch all the modules installed on the OpenERP server
        module_obj = self._oerp.get('ir.module.module')
        module_ids = module_obj.search([('state', '=', 'installed')])
        for data in module_obj.read(module_ids, ['name']):
            if data['name'] not in modules:
                modules_full[data['name']] = {
                    'models': [],
                    'depends': [],
                    'keep': keep,
                }
        # Dispatch data models in their related modules
        for model, data in models.iteritems():
            for module in data['modules']:
                if module in modules_full \
                        and model not in modules_full[module]['models']:
                    modules_full[module]['models'].append(model)
        # Compute the list of modules related to data models
        if restrict:
            for model, data in models.iteritems():
                for module in data['modules']:
                    if module not in modules:
                        modules[module] = {
                            'models': [],
                            'depends': [],
                            'keep': keep,
                        }
                    if model not in modules[module]['models']:
                        modules[module]['models'].append(model)
        # Otherwise, just take the full list of modules
        else:
            modules = copy.deepcopy(modules_full)
        return modules, modules_full

    def _scan_module_dependencies(self, root_modules):
        """Scan dependencies of modules, until reaching each node in
        `root_modules`.  If `root_modules` is empty, dependencies of all
        installed modules will be computed.
        """
        module_obj = self._oerp.get('ir.module.module')
        # Compute dependencies of all installed modules
        for name in self._modules_full:
            module_ids = module_obj.search([('name', '=', name)])
            module = module_obj.browse(module_ids[0])
            for dependency in module.dependencies_id:
                if dependency.name in self._modules_full:
                    self._modules_full[name]['depends'].append(dependency.name)
                if name in self._modules and dependency.name in self._modules:
                    self._modules[name]['depends'].append(dependency.name)
        # In restrict mode, fix modules similar to "root" module (with no direct
        # dependency) while they may have indirect dependencies
        if self._restrict:
            for name, data in self._modules.items():  # Avoid iter modification
                # Detect fake "root" module
                if not data['depends'] and self._modules_full[name]['depends']:
                    self._fix_fake_root_module(name)
        # Mark modules to keep in the graph if they belong to a path
        # leading to one of the starting modules
        for module in root_modules:
            if module not in self._modules_full:
                raise error.InternalError(
                    "'{0}' module does not exist".format(module))
        for module in self._modules:
            queue = []
            queue.append(module)
            # Recursive function to scan the graph and keep modules
            def process_keep(queue, module):
                for depend in self._modules[module]['depends']:
                    queue.append(depend)
                    # Found? Keep modules concerned by this path
                    if depend in root_modules:
                        for mod in queue:
                            self._modules[mod]['keep'] = True
                        break
                    else:
                        process_keep(queue, depend)
                queue.pop()
            process_keep(queue, module)

    def _fix_fake_root_module(self, module):
        """Fix the fake root `module` by finding its indirect dependencies."""
        def find_path(path, mod):
            """Try to found a path from the module `mod` among all installed
            modules to reach any 'restricted' module.
            """
            path.append(mod)
            for depend in self._modules_full[mod]['depends']:
                path.append(depend)
                if depend in self._modules:
                    # The 'head' module must have a common data model with the
                    # 'tail' one.
                    mod_tail = self._modules[module]['models']
                    mod_head = self._modules[depend]['models']
                    if list(set(mod_tail) & set(mod_head)):
                        return True
                path.pop()
                return find_path(path, depend)
            path.pop()
            return False

        path = []
        found_ok = find_path(path, module)
        # Update the graph by adding required modules to satisfy the
        # indirect dependency
        if found_ok:
            for index, mod in enumerate(path):
                if mod not in self._modules:
                    # Add the required module, but without its dependencies
                    self._modules[mod] = copy.deepcopy(self._modules_full[mod])
                    for depend in self._modules[mod]['depends'][:]:
                        if depend not in self._modules:
                            self._modules[mod]['depends'].remove(depend)
                    self._modules[mod]['comment'] = \
                        "Indirect dependency"
                    # Add the current module as a dependency to the previous one
                    previous_mod = path[index - 1]
                    if mod not in self._modules[previous_mod]['depends']:
                        self._modules[previous_mod]['depends'].append(mod)

    @staticmethod
    def _draw_graph_node(module, tpl):
        """Generates a Graphviz node named `module`."""
        import pydot
        return pydot.Node(module, margin='0', shape='none', label=tpl)

    @staticmethod
    def _draw_graph_edge(parent, child):
        """Generates a Graphviz edge between `parent` and `child` modules."""
        import pydot
        return pydot.Edge( parent, child, dir='back')

    def make_dot(self):
        """Returns a `pydot.Dot` object representing dependencies
        between modules.

            >>> graph = oerp.inspect.dependencies(['base'], ['res.partner'])
            >>> graph.make_dot()
            <pydot.Dot object at 0x2f01990>

        See the `pydot <http://code.google.com/p/pydot/>`_ documentation
        for details.
        """
        try:
            import pydot
        except ImportError:
            raise error.InternalError("'pydot' module not found")
        output = pydot.Dot()

        def get_template(module, data):
            """Generate the layout of the module."""
            root = all(not self._modules[depend]['keep']
                       for depend in data['depends'])
            # Model lines
            tpl_models = []
            for model in data['models']:
                tpl_models.append(TPL_MODULE_MODEL.format(
                    color_model=self._config['color_model'], model=model))
            # Module comment
            tpl_comment = None
            if data.get('comment'):
                tpl_comment = "<tr><td> </td></tr>"
                tpl_comment += TPL_MODULE_COMMENT.format(
                    color_comment=self._config['color_comment'],
                    comment=data['comment'])
            # Module
            color_module_title = self._config['color_module_title']
            bgcolor_module_title = self._config['bgcolor_module_title']
            if root:
                color_module_title = self._config['color_module_title_root']
                bgcolor_module_title = self._config['bgcolor_module_title_root']
            if not root and tpl_models:
                color_module_title = \
                    self._config['color_module_title_highlight']
                bgcolor_module_title = \
                    self._config['bgcolor_module_title_highlight']
            tpl = TPL_MODULE.format(
                color_module_title=color_module_title,
                bgcolor_module_title=bgcolor_module_title,
                bgcolor_module=self._config['bgcolor_module'],
                name=module.upper(),
                models=''.join(tpl_models),
                comment=tpl_comment or '')
            return tpl

        for module, data in self._modules.iteritems():
            if not data['keep']:
                continue
            # Add the module as node
            tpl = get_template(module, data)
            node = self._draw_graph_node(module, tpl)
            output.add_node(node)
            for dependency in data['depends']:
                if not self._modules[dependency]['keep']:
                    continue
                # Add edge between the module and it's dependency
                edge = self._draw_graph_edge(dependency, module)
                output.add_edge(edge)

        return output

    def write(self, *args, **kwargs):
        """Write the resulting graph in a file.
        It is just a wrapper around the :func:`pydot.Dot.write` method
        (see the `pydot <http://code.google.com/p/pydot/>`_ documentation for
        details).  Below a common way to use it::

            >>> graph = oerp.inspect.dependencies(['res.partner'])
            >>> graph.write('dependencies_res_partner.png', format='png')
        
        About supported formats, consult the
        `Graphviz documentation <http://www.graphviz.org/doc/info/output.html>`_.
        """
        output = self.make_dot()
        return output.write(*args, **kwargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
