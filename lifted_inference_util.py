from collections import defaultdict
from itertools import *
from unionfind import UnionFind
from query import *


def is_ground_atom(cnf):
    return len(cnf.items) == 1 and len(cnf.items[0].items) == 1 and cnf.items[0].items[0].isgrounded()

def perform_cancellations(ucnf):
    # TODO: There's a lot more possible cancellations that can be done
    # First pass: unify variables in every cnf
    # Second pass: Reduce cnfs of the form S(x,y), S(x,y) to just a single S(x,y)
    # Third pass: eliminate redundant cnfs of form [S(x,y), T(x)] || S(x,y) to T(x) || S(x,y)
    ucnf = ucnf.makecopy()

    for i, cnf in enumerate(ucnf.items):
        ucnf.items[i] = get_unified_cnf(cnf)

    for cnf in ucnf.items:
        single_literals = set()
        new_disjs = []
        for clause in cnf.items:
            if len(clause.items) > 1:
                new_disjs.append(clause)
            else:
                isduplicate = False
                currentliteral = clause.items[0]
                for literal in single_literals:
                    if isduplicate:
                        break
                    if literal.tableName == currentliteral.tableName:
                        isduplicate = True
                        for i, var in enumerate(literal.variables):
                            if var.getname() != currentliteral.variables[i].getname():
                                isduplicate = False
                                break
                if not isduplicate:
                    single_literals.add(currentliteral)
                    new_disjs.append(clause)
        cnf.items = new_disjs

    nuts = []
    newcnfs = []
    for cnf in ucnf.items:
        if len(cnf.items) == 1:
            if len(cnf.items[0].items) == 1:
                nuts.append(cnf.items[0].items[0])
                newcnfs.append(cnf)

    for cnf in ucnf.items:
        gotonextcnf = False
        newcnfs.append(cnf)
        for clause in cnf.items:
            if len(clause.items) == 1:
                for nut in nuts:
                    # TODO: probably need to check that the variables are the same as well
                    if nut.tableName == clause.items[0].tableName:
                        newcnfs.pop()
                        gotonextcnf = True
                        break
            if gotonextcnf:
                break
    ucnf.items = newcnfs
    return ucnf

def get_connected_components(clause):
    """Helper for Step 1 of LI: convert cnf to ucnf. Gets number of connected components.

    Args:
        clause (Disj): disjunction of tuples

    Returns:
        (int): number of connected components

    """
    # We are basically dividing variables into separate disjoint sets, each representing variables in a component.
    # Then, we go through each set and find the tuples that contain these variables to return the components.
    uf = UnionFind()
    var_to_tuples = defaultdict(set)
    # Keep track of components that are fully grounded separately, since it is easier to work with this way.
    connected_grounded_components = set()
    for tuple in clause.items:
        # If the tuple is fully grounded, it is its own connected component
        if tuple.isgrounded():
            connected_grounded_components.add(tuple)
            # connected_components += 1
            continue

        # Every tuple has variables
        tuple_variables = tuple.variables

        # Get the first variable in the tuple and add it to the disjoint set
        for i, variable in enumerate(tuple_variables):
            if not variable.is_constant:
                first_ungrounded_variable = variable.name
                first_ungrounded_variable_index = i
                uf.add(first_ungrounded_variable)
                var_to_tuples[first_ungrounded_variable].add(tuple)
                break

        # Add the rest of the variables to the same disjoint set as the first ungrounded variable
        for variable in tuple_variables[first_ungrounded_variable_index + 1:]:
            uf.union(first_ungrounded_variable, variable.name)
            var_to_tuples[variable.name].add(tuple)

    ungrounded_components = uf.components() if len(uf) > 0 else []
    connected_components = [set([tuple]) for tuple in connected_grounded_components]
    for component in ungrounded_components:
        component_tuples = set()
        for variable in component:
            for tuple in var_to_tuples[variable]:
                component_tuples.add(tuple)
        connected_components.append(component_tuples)

    return connected_components

# TODO: Still need to handle cancellations
def convert_to_ucnf(cnf):
    """For Step 1 of LI: convert cnf to ucnf

    Args:
        cnf (Conj): cnf to convert to ucnf. Must be a valid cnf, whose items are all disjunctions of tuples.

    Returns:
        ucnf (Disj): ucnf

    """

    # TODO: Handle negation? -> Need to double check, but I don't think we'll ever have a negated query at this point

    if len(cnf.items) == 1:
        return Disj([Conj([Disj(list(i))]) for i in get_connected_components(cnf.items[0])])

    for i, clause in enumerate(cnf.items):
        if len(get_connected_components(clause)) >= 2:
            cnf.items.pop(i)
            ucnf_rest = convert_to_ucnf(cnf)

            fin = []
            for conj in ucnf_rest.items:
                for j in clause.items:
                    fin.append(Conj(conj.items + [Disj([j])]))
            return perform_cancellations(Disj(fin))
            # return Disj([Conj(conj.items + [j]) for conj in ucnf_rest.items for j in clause.items])

    # If we reach here, then none of the clauses has 2 or more connected components
    return Disj([cnf])

def get_decomposable_disjunction(ucnf):
    """For Step 2 of LI: get two independent queries if possible

    Args:
        ucnf (Disj):

    Returns:
        (None | tuple of cnf, cnf): two independent cnfs, or None if there are none

    """

    # TODO: handle constants
    if len(ucnf.items) != 2:
        return None

    l1set = ucnf.items[0].gettablenames()
    l2set = ucnf.items[1].gettablenames()

    if (len(l1set | l2set) == len(l1set) + len(l2set)) or not ucnf.items[0].getungroundedvariablenames() or not ucnf.items[1].getungroundedvariablenames():
        return ucnf.items[0], ucnf.items[1]

    return None

def can_perform_inclusion_exclusion(ucnf):
    return len(ucnf.items) > 1

def combos(x):
    """Returns all subsets of list x. Used in inclusion / exclusion
    """
    if len(x) == 0:
        return []
    cs = combos(x[1:])
    return [(x[0],)] + [(x[0],) + c for c in cs] + cs

def perform_inclusion_exclusion(ucnf):
    """For Step 3 of LI: Inclusion / Exclusion

    Note: Should only be called if Step 2 fails

    Args:
        ucnf (Disj): ucnf consisting more than 1 cnfs

    Returns:
        todo: fill this out

    """
    if not can_perform_inclusion_exclusion(ucnf):
        raise Exception('Cannot perform inclusion / exclusion. Be sure to call can_perform_inclusion_exclusion() first.')

    res = Sum()
    subsets = combos(ucnf.items)
    for subset in subsets:
        res.operands.append([reduce(lambda x, y: Conj(x.items + y.items), subset), len(subset) % 2 == 1])

    return res

def get_decomposable_conjunction(ucnf):
    """For Step 4 of LI: get two independent queries from a single cnf

    Note: Should only be called if Step 2 and Step 3 fail (and thus our ucnf consists only of a single cnf)

    Args:
        ucnf (Disj): ucnf consisting only of a single cnf

    Returns:
        (None | tuple of Conj, Conj): two independent CNFs, or None if there are none

    """
    # TODO: handle constants
    if len(ucnf.items) != 1:
        return None

    l1 = []
    l2 = []
    for pattern in product([True, False], repeat=len(ucnf.items[0].items)):
        # l1 and l2 are each a list of clauses
        l1.clear()
        l2.clear()
        l1 += ([x[1] for x in zip(pattern, ucnf.items[0].items) if x[0]])
        l2 += ([x[1] for x in zip(pattern, ucnf.items[0].items) if not x[0]])

        l1set = reduce((lambda x, y: x | y), [set()] + [item.gettablenames() for item in l1])
        l2set = reduce((lambda x, y: x | y), [set()] + [item.gettablenames() for item in l2])

        if len(l1set | l2set) == len(l1set) + len(l2set) and len(l1set) != 0 and len(l2set) != 0:
            return Conj(l1), Conj(l2)

    return None

def get_unified_cnf(cnf):
    # keep a global mapping of Tuples and their variables
    # Also keep a local mapping of variables
    cnf = cnf.makecopy()
    tupletovars = {}
    for clause in cnf.items:
        varmapping = {}
        seen_tuples = []
        unseen_tuples = []
        for tuple in clause.items:
            if tuple.tableName not in tupletovars:
                unseen_tuples.append(tuple)
            else:
                seen_tuples.append(tuple)

        for tuple in seen_tuples:
            variables = tupletovars[tuple.tableName]
            for i, variable in enumerate(variables):
                if not variable.is_constant and not tuple.variables[i].is_constant:
                    varmapping[tuple.variables[i].getname()] = variable.getname()
                    tuple.variables[i].setname(variable.getname())

        for tuple in unseen_tuples:
            for var in tuple.variables:
                if var.getname() in varmapping:
                    var.setname(varmapping[var.getname()])
                else:
                    varmapping[var.getname()] = var.getname()
            tupletovars[tuple.tableName] = tuple.variables

    return cnf

def decompose_universal_quantifier(ucnf):
    """For Step 5 of LI: get separator variable, if possible

    Args:
        ucnf (Disj):

    Returns:
        None | tuple of separator (string): name of separator variable | query with separator variable grounded

    """
    # Note: In the version of the algorithm that the instructor gives us, we are guaranteed to have
    # a ucnf with only a single cnf at this point of the algorithm. In the version the TAs gave us, we
    # are not. I'm just going to assume we have a single cnf for now, and fix it later if necessary.
    ucnf = Disj([get_unified_cnf(ucnf.items[0])], negate=ucnf.negate)

    intersection = reduce((lambda x, y: x.intersection(y)), [i.getungroundedvariablenames() for j in ucnf.items[0].items for i in j.items])
    if len(intersection) > 0:
        # Convert to a list since sets do not support indexing
        intersection = list(intersection)
        return intersection[0], ground_variable(ucnf, intersection[0]).items[0]

    # TODO: add functionality for unifying variables if there is no obvious separator

    return None

def ground_variable(ucnf, varname):
    '''
    Grounds the variable var by modifying the input ucnf

    :param ucnf (disj):
    :param var (string): variable to ground
    :return:
    '''
    ucnf = ucnf.makecopy()

    for cnf in ucnf.items:
        for clause in cnf.items:
            for tuple in clause.items:
                for variable in tuple.variables:
                    if variable.getname() == varname:
                        variable.setconstant(True)
                        tuple.recheckisgrounded()

    return ucnf