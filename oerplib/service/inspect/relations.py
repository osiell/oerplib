# -*- coding: utf-8 -*-

import re

import pydot

from oerplib import error

TPL_MODEL = """<
<table cellborder="0" cellpadding="0" cellspacing="0"
       border="1" bgcolor="{bgcolor_model}" height="100%%">
    <tr>
        <td border="0" bgcolor="{bgcolor_model_title}" align="center" colspan="2">
            <font color="{color_model_title}">{name}</font>
        </td>
    </tr>
    {attrs}
    {relations_r}
</table>>"""

TPL_MODEL_ATTR = """
<tr>
    <td align="left" border="0">- <font color="{color}">{name}</font></td>
    <td align="left" border="0"> <font color="{color}">{type_}</font></td>
</tr>
"""

TPL_MODEL_HEADER_REL_R = """
<tr><td> </td></tr>
<tr>
    <td align="center"
        border="0"
        colspan="2"><font color="{color}">[Recursive relations]</font></td>
</tr>
"""

TPL_MODEL_REL_R = """
<tr>
    <td align="left" border="0" colspan="2">- {name}</td>
</tr>
"""


def elt2regex(elt):
    return re.compile(elt.replace('*', '.*'))


def match_in(elt, lst):
    for regex in lst:
        if regex.match(elt):
            return True
    return False


class Relations(object):
    """Draw relations between models with `Graphviz`."""
    def __init__(self, oerp, model, maxdepth=1, whitelist=None, blacklist=None,
                 config=None):
        self._oerp = oerp
        self._model = model
        self._obj = self._oerp.get(model)
        self._maxdepth = maxdepth
        self._whitelist = map(elt2regex, whitelist or [])
        self._blacklist = map(elt2regex, blacklist or [])
        # Configuration options
        self._config = {
            'relation_types': ['many2one', 'one2many', 'many2many'],
            'show_many2many_table': False,
            'show_model_attrs': True,
            'color_many2one': '#0E2548',
            'color_one2many': '#008200',
            'color_many2many': '#6E0004',
            'bgcolor_model_title': '#64629C',
            'color_model_title': 'white',
            'bgcolor_model': 'white',
            'color_normal': 'black',
            'color_required': 'blue',
            'space_between_models': 0.25,
        }
        self._config.update(config or {})
        # Dot graph
        self._graph = pydot.Dot(
            graph_type='digraph', overlap='scalexy', splines='true',
            nodesep=str(self._config['space_between_models']))
        # Store relations between data models:
        self._relations = {}
        self._stack = {'o2m': {}}
        # Build and draw relations
        self._build_relations(self._obj, 0)
        self._draw_relations()

    def _build_relations(self, obj, depth):
        """Build all relations of `obj` recursively:
            - many2one
            - one2many (will be bound to the related many2one)
            - many2many (will be bound with the eventual many2many from the
              other side)
        """
        # Stop scanning when the maxdepth is reached, or when the data model
        # has already been scanned
        if depth > self._maxdepth or obj._name in self._relations:
            return
        # Check the whitelist, then the blacklist
        if obj._name != self._model:
            if self._whitelist:
                if not match_in(obj._name, self._whitelist):
                    return
            if self._blacklist:
                if match_in(obj._name, self._blacklist):
                    return
        # Only increments depth for data models which are not already scanned
        if obj._name not in self._relations:
            depth += 1
        # Scan relational fields of the data model
        fields = obj.fields_get()
        if obj._name not in self._relations:
            self._relations[obj._name] = {
                'relations': {},
                'relations_r': {},  # Recursive relations
                'obj': obj,
                'fields': dict((k, v) for k, v in fields.iteritems()
                               if not v.get('relation')),
            }
        for name, data in fields.iteritems():
            if 'relation' in data \
                    and data['type'] in self._config['relation_types']:
                rel = data['relation']
                # where to store the relation?
                store_type = obj._name == rel and 'relations_r' or 'relations'
                # many2one
                if data['type'] == 'many2one':
                    # Check if related one2many fields have been registered
                    # for the current many2one relation
                    o2m_fields = obj._name in self._stack['o2m'] \
                        and rel in self._stack['o2m'][obj._name] \
                        and name in self._stack['o2m'][obj._name][rel] \
                        and self._stack['o2m'][obj._name][rel][name] \
                        or []
                    # Add the field
                    self._relations[obj._name][store_type][name] = {
                        'type': 'many2one',
                        'relation': rel,
                        'name': name,
                        'o2m_fields': o2m_fields,
                    }
                # one2many
                elif data['type'] == 'one2many':
                    # 'relation_field' key may be missing for 'one2many'
                    # generated by 'fields.function'
                    rel_f = data.get('relation_field', None)
                    # If it is a normal o2m field (with a relation field), it
                    # will be attached to its corresponding m2o field
                    if rel_f:
                        # Case where the related m2o field has already been
                        # registered
                        if rel in self._relations \
                                and rel_f in self._relations[rel][store_type]:
                            if name not in self._relations[
                                    rel][store_type][rel_f]:
                                self._relations[
                                    rel][store_type][
                                        rel_f]['o2m_fields'].append(name)
                        # Otherwise, we will process the field later (when the
                        # m2o field will be scanned)
                        else:
                            if rel not in self._stack['o2m']:
                                self._stack['o2m'][rel] = {}
                            if obj._name not in self._stack['o2m'][rel]:
                                self._stack['o2m'][rel][obj._name] = {}
                            if rel_f not in self._stack['o2m'][rel][obj._name]:
                                self._stack['o2m'][rel][obj._name][rel_f] = []
                            self._stack[
                                'o2m'][rel][obj._name][rel_f].append(name)
                    # If the o2m field has no relation field available
                    # (calculated by a function, or a related field) the
                    # relation is stored as a standalone one2many
                    else:
                        self._relations[obj._name][store_type][name] = {
                            'type': 'one2many',
                            'relation': rel,
                            'name': name,
                        }
                # many2many
                elif data['type'] == 'many2many':
                    rel_columns = data.get('related_columns')
                    rel_columns = rel_columns and tuple(rel_columns) or None
                    self._relations[obj._name][store_type][name] = {
                        'type': 'many2many',
                        'relation': rel,
                        'name': name,
                        'third_table': data.get('third_table'),
                        'related_columns': None,
                    }
                # Scan relations recursively
                rel_obj = self._oerp.get(rel)
                self._build_relations(rel_obj, depth)

    def _draw_relations(self):
        """Generate the graphic."""
        for model, data in self._relations.iteritems():
            # Generate attributes of the model
            attrs = []
            if self._config['show_model_attrs']:
                for k, v in data['fields'].iteritems():
                    color = v.get('required') \
                        and self._config['color_required'] \
                        or self._config['color_normal']
                    attr = TPL_MODEL_ATTR.format(
                        name=k, color=color, type_=v['type'])
                    attrs.append(attr)
            # Generate recursive relations of the model
            relations_r = []
            if data['relations_r']:
                header_rel_r = TPL_MODEL_HEADER_REL_R.format(
                    color=self._config['color_normal'])
                relations_r.append(header_rel_r)
            for name, data2 in data['relations_r'].iteritems():
                label = self._generate_relation_label(data2)
                rel_r = TPL_MODEL_REL_R.format(name=label)
                relations_r.append(rel_r)
            # Generate the layout of the model
            tpl = TPL_MODEL.format(
                color_model_title=self._config['color_model_title'],
                bgcolor_model_title=self._config['bgcolor_model_title'],
                bgcolor_model=self._config['bgcolor_model'],
                name=model,
                attrs=''.join(attrs),
                relations_r=''.join(relations_r))
            # Add the model to the graph
            node = (data['obj']._name, 'relation', tpl)
            self._graph.add_node(self._create_node(*node))
            # Draw relations of the model
            for name, data2 in data['relations'].iteritems():
                if data2['relation'] in self._relations:
                    rel_obj = self._relations[data2['relation']]['obj']
                    edge = (data['obj'], rel_obj, data2)
                    self._graph.add_edge(self._create_edge(*edge))

    def _create_node(self, name, type_, tpl=None):
        """Generate a `pydot.Node` object.
        `type_` can take one of these values: ``relation``, ``m2m_table``.
        If a HTML `tpl` is supplied, it will be used as layout for the node.
        """
        types = {
            'relation': {
                'margin': '0',
                'shape': tpl and 'none' or 'record',
                'label': tpl or name,
            },
            'm2m_table': {
                'margin': '0',
                'shape': tpl and 'none' or 'record',
                'color': self._config['color_many2many'],
                'fontcolor': self._config['color_many2many'],
                'label': tpl or name,
            },
        }
        return pydot.Node(name, **types[type_])

    def _create_edge(self, obj1, obj2, data):
        """Generate a `pydot.Edge` object, representing a relation between
        `obj1` and `obj2`.
        """
        label = self._generate_relation_label(data, space=6, closing_tag=True)
        kwargs = {
            'label': label,
            'labeldistance': '10.0',
            'color': self._config['color_{0}'.format(data['type'])],
            'fontcolor': self._config['color_{0}'.format(data['type'])],
            #'arrowhead': data['type'] == 'many2many' and 'none' or 'normal',
        }
        return pydot.Edge(obj1._name, obj2._name, **kwargs)

    def _generate_relation_label(self, data, space=0, closing_tag=False):
        """Generate a HTML label based for the relation described by `data`."""
        name_color = data.get('required') \
            and self._config['color_required'] \
            or self._config['color_{0}'.format(data['type'])]
        label = "{space}<font color='{color}'>{name}</font>".format(
            color=name_color, name=data['name'], space=' ' * space)
        # many2one arrow
        if data['type'] == 'many2one' and data['o2m_fields']:
            label = "{label} <font color='{color}'>← {o2m}</font>".format(
                label=label,
                color=self._config['color_one2many'],
                o2m=', '.join(data['o2m_fields']))
        # one2many "standalone" arrow
        if data['type'] == 'one2many':
            pass
        # many2many arrow
        if data['type'] == 'many2many':
            m2m_table = ''
            if self._config['show_many2many_table']:
                rel_name = data.get('third_table') or 'CALCULATED'
                m2m_table = '({rel_name})'.format(rel_name=rel_name)
            label = "{space}<font color='{color}'>{name}<br/>{m2m_t}</font>".format(
                color=name_color, name=data['name'],
                m2m_t=m2m_table, space=' ' * space)
            #self._graph.add_node(self._create_node(rel_name, 'm2m_table'))
        label = label + "{space}".format(space=' ' * space)
        if closing_tag:
            label = "<{label}>".format(label=label)
        return label

    def write(self, *args, **kwargs):
        """Write the resulting graph in a file.
        It is just a wrapper around the :func:`pydot.Dot.write` method. See the
        `pydot` documentation for details.
        """
        return self._graph.write(*args, **kwargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
