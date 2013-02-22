# -*- coding: utf-8 -*-

import pydot

COLORS = {
    'many2one': "blue",
    'one2many': "red",
    'many2many': "purple",
}


class Relations(object):
    """TODO"""
    def __init__(self, oerp, model, maxdepth=1, blacklist=None, whitelist=None,
                 rel_types=None):
        if blacklist and whitelist:
            raise error.InternalError(
                "'blacklist' and 'whitelist' parameters can not be set "
                "simultaneously")
                #"Blacklist and whitelist parameters can't be defined together.")
        self._oerp = oerp
        self._model = model
        self._obj = self._oerp.get(model)
        self._maxdepth = maxdepth
        self._blacklist = blacklist or []
        self._whitelist = whitelist or []
        self._rel_types = rel_types or ['many2one', 'many2many']
        self._graph = pydot.Dot(graph_type='digraph')
        self._relations = {}
        # Generate the graphic
        self._draw(self._obj, 0, self._maxdepth)

    def _save_relation(self, obj1, obj2, field, rel_type, rel_fields=None):
        if obj1._name not in self._relations:
            self._relations[obj1._name] = {}
        if obj2._name not in self._relations[obj1._name]:
            self._relations[obj1._name][obj2._name] = []
        if field not in self._relations[obj1._name][obj2._name]:
            self._relations[obj1._name][obj2._name].append(field)

    def _has_relation(self, obj1, obj2, field, rel_type=None, rel_fields=None):
        return obj1._name in self._relations \
                and obj2._name in self._relations[obj1._name] \
                and field in self._relations[obj1._name][obj2._name]

    def _draw(self, obj, depth, maxdepth):
        # Stop drawing when the maxdepth is reached
        if depth >= maxdepth:
            return
        # Draw obj and its relations
        fields = obj.fields_get()
        self._graph.add_node(self._create_node(obj, fields))
        depth += 1
        for name, data in fields.iteritems():
            if 'relation' in data:
                rel_obj = self._oerp.get(data['relation'])
                # Skip the relation if it has already been drawn
                if self._has_relation(obj, rel_obj, name):
                    continue
                if data['type'] in self._rel_types:
                    # Keep the relation
                    self._save_relation(obj, rel_obj, name, data['type'])
                    # Draw the relation
                    node = (rel_obj, rel_obj.fields_get())
                    edge = (obj, rel_obj, name, data['type'])
                    self._graph.add_node(self._create_node(*node))
                    self._graph.add_edge(self._create_edge(*edge))
                    self._draw(rel_obj, depth, maxdepth)

    def _create_node(self, obj, fields):
        label = """<<table border="0" cellborder="0" cellpadding="0"
                        bgcolor="white" width="100%%" height="100%%">
            <tr>
                <td border="1" bgcolor="black" align="center">
                    <font color="white">%s</font>
                </td>
            </tr>
            <tr>
                <td></td>
            </tr>
        </table>>""" % obj._name
        return pydot.Node(obj._name, margin="0", shape="rectangle", label=label)

    def _create_edge(self, obj1, obj2, label, type_):
        color = COLORS[type_]
        return pydot.Edge(obj1._name, obj2._name, label=label, color=color)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
