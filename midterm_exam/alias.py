from lang import *
from functools import reduce
from abc import ABC, abstractmethod


class Edge:
    """
    This class implements the edge of the points-to graph that is used to
    solve Andersen-style alias analysis.
    """

    def __init__(self, dst, src):
        """
        An edge src -> dst indicates that every pointer in src must be also
        within the alias set of dst.
        """
        self.src = src
        self.dst = dst

    def eval(self, env):
        """
        Evaluating an edge such as dst -> src means copying every pointer in
        Alias(dst) into Alias(src). This function returns True if the
        points-to set of dst changes after the evaluation.

        Example:
            >>> e = Edge('a', 'b')
            >>> env = {'a': {'ref_1'}, 'b': {'ref_0'}}
            >>> result = e.eval(env)
            >>> f"{result}: {sorted(env['a'])}"
            "True: ['ref_0', 'ref_1']"
        """
        destination_alias_set = env.get(self.dst, set())
        source_alias_set = env.get(self.src, set())

        new_destination_alias_set = source_alias_set.union(destination_alias_set)
        env[self.dst] = set(sorted(new_destination_alias_set))

        return bool(set(new_destination_alias_set).difference(destination_alias_set))

    def __str__(self):
        """
        The string representation of an edge.

        Example:
            >>> e = Edge('a', 'b')
            >>> str(e)
            'Alias(a) >= Alias(b)'
        """
        return f"Alias({self.dst}) >= Alias({self.src})"


def init_env(insts):
    """
    Uses the basic constraints derived from alloca instructions to initialize
    the environment.

    Example:
        >>> Inst.next_index = 0
        >>> i0 = Alloca('v')
        >>> i1 = Alloca('v')
        >>> i2 = Alloca('w')
        >>> sorted(init_env([i0, i1, i2])['v'])
        ['ref_0', 'ref_1']
    """
    env = {}
    counter = -1

    for instruction in insts:
        counter += 1

        # if instruction is not an initialization constraint, move to the next inst
        if not isinstance(instruction, Alloca):
            continue

        new_memory_location = f"ref_{counter}"

        if env.get(instruction.name):
            current_set = env.get(instruction.name)
            # the allocation name already exists
            current_set.add(new_memory_location)
        else:
            # create new entry in the environment
            env.setdefault(instruction.name, {new_memory_location})

        # add entry for the new memory location
        env.setdefault(new_memory_location, set())

    return env


def propagate_alias_info(edges, env):
    """
    Propagates all the points-to information along the edges of the points-to
    graph once. If any points-to set changes, then this function returns true;
    otherwise, it returns false.

    Example:
        >>> e0 = Edge('b', 'a')
        >>> e1 = Edge('y', 'x')
        >>> env = {'a': {'v0'}, 'x': {'v2'}}
        >>> changed = propagate_alias_info([e0, e1], env)
        >>> f"{changed, env['y'], env['b']}"
        "(True, {'v2'}, {'v0'})"

        >>> e = Edge('b', 'a')
        >>> env = {'a': {'v0'}, 'b': {'v0'}}
        >>> changed = propagate_alias_info([e], env)
        >>> f"{changed, env['a'], env['b']}"
        "(False, {'v0'}, {'v0'})"
    """
    some_points_to_set_changed = False

    for edge in edges:
        points_to_set_changed = edge.eval(env)

        if points_to_set_changed:
            some_points_to_set_changed = True

    return some_points_to_set_changed


def evaluate_mv_constraints(insts):
    new_edges = []

    for instruction in insts:
        # if instruction is not a move constraint, move to the next inst
        if not isinstance(instruction, Move):
            continue

        if instruction.src != instruction.dst:
            new_edges.append(Edge(instruction.dst, instruction.src))

    return new_edges


def evaluate_st_constraints(insts, env):
    """
    A store constraint is created by an instruction such as *ref = src. To
    evaluate a constraint like this, we do as follows: for each t in ref, we
    create a new edge src -> t. The result of evaluating this constraint is a
    new set of edges. This function returns all the edges Edge(src, t), such
    that t is in the points to set of ref.

    Example:
        >>> Inst.next_index = 0
        >>> i0 = Store('b', 'a') # *b = a
        >>> i1 = Store('y', 'x') # *y = x
        >>> env = {'b': {'r'}, 'y': {'x', 's'}}
        >>> edges = evaluate_st_constraints([i0, i1], env)
        >>> sorted([str(edge) for edge in edges])
        ['Alias(r) >= Alias(a)', 'Alias(s) >= Alias(x)']
    """
    new_edges = []

    for instruction in insts:
        # if instruction is not a store constraint, move to the next inst
        if not isinstance(instruction, Store):
            continue

        current_ref_alias_set = env.get(instruction.ref, set())

        # empty set, move on
        if not current_ref_alias_set:
            continue

        for points_to_element in current_ref_alias_set:
            # information is already flowing in this node, there is no need to create an edge from x -> x
            if points_to_element == instruction.src:
                continue

            new_edge = Edge(points_to_element, instruction.src)
            new_edges.append(new_edge)

    return new_edges


def evaluate_ld_constraints(insts, env):
    """
    A load constraint is created by an instruction such as dst = *ref. To
    evaluate a constraint like this, we do as follows: for each t in ref, we
    create a new edge t -> dst. The result of evaluating this constraint is a
    new set of edges. This function, like evaluate_st_constraints, returns
    the set of edges t -> dst, such that t is in th points-to set of ref.

    Example:
        >>> Inst.next_index = 0
        >>> i0 = Load('b', 'a') # b = *a
        >>> i1 = Load('y', 'x') # y = *x
        >>> env = {'a': {'r'}, 'x': {'y', 's'}}
        >>> edges = evaluate_ld_constraints([i0, i1], env)
        >>> sorted([str(edge) for edge in edges])
        ['Alias(b) >= Alias(r)', 'Alias(y) >= Alias(s)']
    """
    new_edges = []

    for instruction in insts:
        # if instruction is not a load constraint, move to the next inst
        if not isinstance(instruction, Load):
            continue

        current_ref_alias_set = env.get(instruction.ref, set())

        # empty set, move on
        if not current_ref_alias_set:
            continue

        for points_to_element in current_ref_alias_set:
            # information is already flowing in this node, there is no need to create an edge from x -> x
            if points_to_element == instruction.dst:
                continue

            new_edge = Edge(instruction.dst, points_to_element)
            new_edges.append(new_edge)

    return new_edges


def abstract_interp(insts):
    """
    This function solves points-to analysis in four steps:
    1. It creates an initial environment with the results of Allocas
    2. It creates an initial points-to graph G with the Move instructions
    3. It iterates the following three steps, while points-to data changes:
       3.a: evaluate all the store constraints, maybe adding new edges to G.
       3.b: evaluate all the load constraints, maybe adding new edges to G.
       3.c: propagate points-to information along the edges of G.

    Example:
        >>> Inst.next_index = 0
        >>> i0 = Alloca('p0')
        >>> i1 = Alloca('p1')
        >>> i2 = Store('p0', 'p1')
        >>> i3 = Load('p2', 'p0')
        >>> i4 = Store('p2', 'one')
        >>> i5 = Move('p3', 'p1')
        >>> i6 = Store('p3', 'two')
        >>> env = abstract_interp([i0, i1, i2, i3, i4, i5, i6])
        >>> env['p0'], env['p1'], env['p2'], env['p3'], env['ref_0']
        ({'ref_0'}, {'ref_1'}, {'ref_1'}, {'ref_1'}, {'ref_1'})
    """
    #
    # 1. Initialize the environment:
    #
    env = init_env(insts)

    # 2. Build the initial graph of points-to relations:
    #
    edges = evaluate_mv_constraints(insts)

    # 3. Run iterations until we stabilize:
    #
    changed = True
    while changed:
        # 3.a: Evaluate all the complex constraints:
        #
        edges += evaluate_st_constraints(insts, env)
        edges += evaluate_ld_constraints(insts, env)

        # 3.b: Propagate the points-to information:
        #
        changed = propagate_alias_info(edges, env)

    return env
