__author__ = 'Nino Bašić <nino.basic@fmf.uni-lj.si>'

from flag_graph import Map
from itertools import *


# Helper functions

def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


class Map(Map):

    def do_trace(self, pos, cross_list):
        size = len(self.flags) // 4
        cross_set = set(cross_list)
        cross_indicator = [i in cross_set for i in range(size)]
        trace = [pos]  # Starting point
        while True:
            pos = pos.t1()
            trace.append(pos)
            pos = pos.t0()
            if cross_indicator[pos.e]:
                pos = pos.t2()
            if pos == trace[0]:
                break
            trace.append(pos)
        return trace


def find_strong_traces(face_list):
    m = Map(face_list)
    primary_flag_id = next(iter(m.flags))
    primary_flag = m.flags[primary_flag_id]

    res = []  # List of results (connected traces)

    for crossover in powerset(m.id_to_edge.keys()):
        trace = m.do_trace(primary_flag, crossover)
        if len(trace) == len(m.flags):
            res.append(trace)

    return res


def short_form():
    pass


def naive_test():
    """
    Test the naive algorithm on tetrahedron.
    """
    from data import tetrahedron
    s_traces = find_strong_traces(tetrahedron)
    print('+-------------+')
    print('| Tetrahedron |')
    print('+-------------+')
    print('Number of traces:', len(s_traces))
    print('Number of non-equivalent traces:', 'NotImplemented')


naive_test()
