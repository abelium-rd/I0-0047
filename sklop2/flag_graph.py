__author__ = 'Nino Bašić <nino.basic@fmf.uni-lj.si>'


"""
A map is a cellular embedding of a graph in a surface. Polyhedral surfaces can
therefore be viewed as maps. Figure 1 show a planar embedding of the octahedron.

Vertices are label by integers 1, 2, ..., 6.

Edges are pairs of vertices and can be represented by tuples: (1, 2), (2, 3), ...

Faces can be given by listing all vertices on some face-walk. The octahedron on
Figure 1 can be given by the list of face-walks -- see octahedron in module data.
We will construct a map from such description.
"""

import networkx
import matplotlib.pyplot


class Flag:
    """
    This class describes a single flag.
    """
    def __init__(self, v, e, f):
        self.v = v
        self.e = e
        self.f = f
        self._t0 = self._t1 = self._t2 = None  # For now.

    def __repr__(self):
        return 'Flag({}, {}, {})'.format(self.v, self.e, self.f)

    def tuple(self):
        return self.v, self.e, self.f

    def t2(self):
        """
        Return the flag with the same vertex and edge, but on different face.
        """
        return self._t2

    def t1(self):
        """
        Return the flag with the same vertex and face, but on different edge.
        """
        return self._t1

    def t0(self):
        """
        Return the flag with the same edge and face, but on different vertex.
        """
        return self._t0

    def debug_str(self):
        return repr(self) + ' -> ' + repr([self.t0(), self.t1(), self.t2()])

    def set_t0(self, flag_object):
        self._t0 = flag_object

    def set_t1(self, flag_object):
        self._t1 = flag_object

    def set_t2(self, flag_object):
        self._t2 = flag_object


class Map:
    """
    This class describes an abstract map (cellular embedding of a graph).

    Warning: This implementation allows only simple graphs.
    """

    def __init__(self, face_list):
        """
        Construct the map from the list of faces. Examples of such lists are octahedron
        and tetrahedron (see above).

        Note: Raises ValueError if the given face_list is illegal.
        """

        self.edges = {}
        self.id_to_edge = {}

        def get_edge_id(edge, edge_dict):
            if edge[0] > edge[1]:
                edge = (edge[1], edge[0])
            if edge not in edge_dict:
                self.id_to_edge[len(edge_dict)] = edge
                edge_dict[edge] = len(edge_dict)
            return edge_dict[edge]

        self.flags = {}

        def add_flag(flag, flag_dict):
            if flag in flag_dict:
                raise ValueError('map description is illegal; flag ({v}, {e}, {f}) appears more than once'.format(
                    v=flag.v, e=flag.e, f=flag.f,
                ))
            flag_dict[(flag.v, flag.e, flag.f)] = flag

        self.face_representative = {}

        for f, face in enumerate(face_list):
            n = len(face)
            for i in range(n):
                u = face[i]
                v = face[(i + 1) % n]
                e = get_edge_id((u, v), self.edges)
                add_flag(Flag(v, e, f), self.flags)
                add_flag(Flag(u, e, f), self.flags)
                # Establish t_0 mapping.
                self.flags[(v, e, f)].set_t0(self.flags[(u, e, f)])
                self.flags[(u, e, f)].set_t0(self.flags[(v, e, f)])

            # Establish t_1 mapping.
            for i in range(n):
                u = face[i]
                e_1 = get_edge_id((u, face[(i + 1) % n]), self.edges)
                e_2 = get_edge_id((face[(i - 1) % n], u), self.edges)
                if i == 0:
                    # Make the list of prepresentatives
                    self.face_representative[f] = self.flags[(u, e_1, f)]
                self.flags[(u, e_1, f)].set_t1(self.flags[(u, e_2, f)])
                self.flags[(u, e_2, f)].set_t1(self.flags[(u, e_1, f)])

        # Establish t_2 mapping and check integrity.
        self.edges_to_flags = {i: [] for i in self.edges.values()}
        for fl in self.flags.values():
            self.edges_to_flags[fl.e].append(fl)

        for i, l in self.edges_to_flags.items():
            u, v = self.id_to_edge[i]
            if len(l) != 4:
                raise ValueError('map description is illegal; edge ({}, {}) should comprise 4 flags instead of {}'.
                                 format(u, v, len(l)))
            l.sort(key=lambda x: x.f)
            if (l[0].f != l[1].f) or (l[2].f != l[3].f) or (l[1].f == l[2].f):
                raise ValueError('map description is illegal; malformed edge ({}, {})'.format(u, v, len(l)))
            l.sort(key=lambda x: x.v)
            if (l[0].v != l[1].v) or (l[2].v != l[3].v) or (l[1].v == l[2].v):
                raise ValueError('map description is illegal; malformed edge ({}, {})'.format(u, v, len(l)))
            l[0].set_t2(l[1])
            l[1].set_t2(l[0])
            l[2].set_t2(l[3])
            l[3].set_t2(l[2])

    def draw(self):
        e_list = []  # List of edges
        color_dict = {}  # List of colors
        for flag in self.flags.values():
            f = flag.tuple()
            fl0 = flag.t0().tuple()
            if fl0 < f:
                e_list.append((fl0, f))
                color_dict[(f, fl0)] = color_dict[(fl0, f)] = 'r'
            fl1 = flag.t1().tuple()
            if fl1 < f:
                e_list.append((fl1, f))
                color_dict[(fl1, f)] = color_dict[(f, fl1)] = 'g'
            fl2 = flag.t2().tuple()
            if fl2 < f:
                e_list.append((fl2, f))
                color_dict[(fl2, f)] = color_dict[(f, fl2)] = 'b'
        g = networkx.Graph(e_list)
        # print(g.order())
        # print(g.size())
        color_list = [color_dict[e] for e in g.edges()]
        networkx.draw(g,
                      pos=networkx.spring_layout(g),
                      edge_color=color_list,
                      width=2.0,
                      with_labels=True,
                      # with_labels=False,
                      node_color='y')
        matplotlib.pyplot.show()
