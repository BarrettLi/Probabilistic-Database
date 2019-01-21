from lifted_inference_util import *

def perform_inference_dnf(dnf):
    cnf = dnf.get_negated_query()
    res = perform_inference(cnf)
    if res:
        res.negate = not res.negate
    return res

def perform_inference(cnf):
    """Performs the Lifted Inference Algorithm on the inputted CNF

    Args:
        cnf (Conj): cnf to perform lifted inference on

    Returns:
        expression representing the reduced query

    """
    # Step 0 Ground Atom
    if is_ground_atom(cnf):
        return cnf.items[0].items[0]

    # Step 1 Convert to ucnf
    ucnf = convert_to_ucnf(cnf)

    # Step 2 Decomposable Disjunction
    decomposed_disj = get_decomposable_disjunction(ucnf)
    if decomposed_disj:
        q1 = perform_inference(decomposed_disj[0])
        q2 = perform_inference(decomposed_disj[1])
        if q1 and q2:
            q1.set_negation(not q1.negate)
            q2.set_negation(not q2.negate)
            return Product([q1, q2], negate=True)

    # Step 3 Inclusion-Exclusion
    if can_perform_inclusion_exclusion(ucnf):
        iesum = perform_inclusion_exclusion(ucnf)
        continueInferring = True
        for i in iesum.operands:
            i[0] = perform_inference(i[0])
            if not i[0]:
                continueInferring = False
                break
        if continueInferring:
            return iesum

    # Step 4 Decomposable Conjunction
    decomposed_conj = get_decomposable_conjunction(ucnf)
    if decomposed_conj:
        q1 = perform_inference(decomposed_conj[0])
        q2 = perform_inference(decomposed_conj[1])
        if q1 and q2:
            return Product([q1, q2])

    # Step 5 Decomposable Universal Quantifier
    sep_var_and_new_cnf = decompose_universal_quantifier(ucnf)
    if sep_var_and_new_cnf:
        seperatedClause = perform_inference(sep_var_and_new_cnf[1])
        if seperatedClause:
            return Pi(sep_var_and_new_cnf[0], seperatedClause)

    # Step 6 Fail
    return None
