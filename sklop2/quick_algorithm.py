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

    @staticmethod
    def traverse_face(flag):
        ret = [flag]
        while True:
            flag = flag.t0()
            ret.append(flag)
            flag = flag.t1()
            if flag == ret[0]:
                break
            ret.append(flag)
        return ret


def label_flags(face_walk, cross, starting_id=1):
    current_id = starting_id
    cross = set(cross)
    labels = []
    for i in range(0, len(face_walk), 2):
        if face_walk[i].e in cross:
            labels.extend([current_id, current_id + 1])
            current_id += 1
        else:
            labels.extend([0, 0])
    pos = len(labels) - 1
    while labels[pos] != current_id:
        pos -= 1
    labels[pos] = starting_id
    return tuple(labels)


def quick_traces(face_list):
    m = Map(face_list)
    # primary_flag_id = next(iter(m.flags))
    # primary_flag = m.flags[primary_flag_id]

    # res = []  # List of results (connected traces)

    n_of_faces = len(m.face_representative)
    meja = dict()
    dp = [{} for _ in range(n_of_faces)]

    # Initial phase
    meja[0] = m.traverse_face(m.face_representative[0])
    all_edges = set([flag.e for flag in meja[0]])
    for crossover in powerset(all_edges):
        if len(crossover) == 0:
            continue
        labels = label_flags(meja[0], crossover)
        dp[0][labels] = 1

    prev_edges = all_edges

    # Keep adding new faces
    for face_num in range(1, n_of_faces - 1):
        print('Adding face number {0} ...'.format(face_num))
        walk = m.traverse_face(m.face_representative[face_num])
        new_edges = set([flag.e for flag in walk])
        meet = new_edges.intersection(prev_edges)
        contacts = set([flag for flag in meja[face_num - 1] if flag.e in meet])
        meja[face_num] = [flag for flag in meja[face_num - 1] + walk if flag.e not in meet]

        for vec in dp[face_num - 1]:
            links = {meja[face_num - 1][i].tuple(): vec[i] for i in range(len(meja[face_num - 1]))}
            cross_option = {i: False for i in meet}
            min_free = 0
            for flag, number in links.items():
                min_free = max(min_free, number + 1)
                if number != 0 and flag[1] in meet:
                    cross_option[flag[1]] = True

            print(min_free)
            print(cross_option)
            print(links)

            for crossover in powerset(new_edges):
                if len(crossover) == 0:
                    continue
                cross_set = set(crossover)
                if not cross_set.intersection(meet) == {x for x, v in cross_option.items() if v is True}:
                    pass  # print('Skipping this face walk ...')
                    continue
                print('Extend with', cross_set)
                new_labels = label_flags(walk, crossover, min_free)
                print(links)
                print(new_labels)

        # Last phase
        prev_edges = new_edges

    print(dp[0])
    return []


def quick_test():
    """
    Test the quick algorithm on tetrahedron.
    """
    from data import tetrahedron
    s_traces = quick_traces(tetrahedron)
    print('+-------------+')
    print('| Tetrahedron |')
    print('+-------------+')
    print('Number of traces:', len(s_traces))
    print('Number of non-equivalent traces:', 'NotImplemented')


quick_test()
