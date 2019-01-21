from lifted_inference_util import *
from query import *

def get_connected_components_test():
    # clause1 = Disj([
    #         Tuple([Variable("x1")], "A"),
    #         Tuple([Variable("x1"), Variable("y1")], "B"),
    #         Tuple([Variable("y1"), Variable("z1")], "C"),
    #         Tuple([Variable("x2"), Variable("y2")], "B"),
    #         Tuple([Variable("y2"), Variable("z2")], "B")
    # ])

    clause2 = Disj([
        Tuple([Variable("x1")], "R"),
        Tuple([Variable("x1"), Variable("y2")], "S"),
        Tuple([Variable("x2"), Variable("y2")], "S"),
        Tuple([Variable("x2")], "T")
    ])

    assert(get_connected_components(clause2) == 2)

def convert_to_ucnf_test():
    # [A(x1) || B(x1, y1) ], C(y1, y2), D(y3, y4)
    cnf1 = Conj([
        Disj([
            Tuple([Variable("x1")], "R"),
            Tuple([Variable("x1"), Variable("y2")], "S")
        ]),
        Disj([
            Tuple([Variable("y1"), Variable("y2")], "C")
        ]),
        Disj([
            Tuple([Variable("y3"), Variable("y4")], "D")
        ])
    ])

    cnf2 = Conj([
        Disj([
            Tuple([Variable("x1", True)], "R"),
            Tuple([Variable("x1", True), Variable("y2")], "S")
        ]),
        Disj([
            Tuple([Variable("x2", True)], "T"),
            Tuple([Variable("x2", True), Variable("y2")], "S")
        ])
    ])

    y = cnf2
    # assert(convert_to_ucnf(cnf1) == [{'y1', 'y2', 'x1'}, {'y4', 'y3'}])
    # x = convert_to_ucnf(cnf2)
    # y = convert_to_ucnf(cnf2)
    # print(len(convert_to_ucnf(cnf2).items))
    x = convert_to_ucnf(cnf2)
    for i in x.items:
        print(i.tostring())
    # print(convert_to_ucnf(cnf2).tostring())
    # print(convert_to_ucnf(cnf2))

def get_decomposable_disjunction_test():
    ucnf1 = Disj([
        Conj([
            Disj([
                Tuple([Variable("x1")], "R"),
                Tuple([Variable("x1"), Variable("y2")], "S")
            ]),
            Disj([
                Tuple([Variable("x2")], "T"),
                Tuple([Variable("x2"), Variable("y2")], "S")
            ])
    ]),
        Conj([
            Disj([
                Tuple([Variable("x2")], "T"),
                Tuple([Variable("x2"), Variable("y2")], "S")
            ])
        ])])

    ucnf2 = Disj([
        Conj([
            Disj([
                Tuple([Variable("x1")], "R"),
                Tuple([Variable("x1"), Variable("y2")], "S")
            ]),
            Disj([
                Tuple([Variable("x2")], "T"),
                Tuple([Variable("x2"), Variable("y2")], "S")
            ])
        ]),
        Conj([
            Disj([
                Tuple([Variable("x2")], "U"),
                Tuple([Variable("x2"), Variable("y2")], "V")
            ])
        ])])

    print("Testing get_decomposable_disjunction_test")
    print("Test 1 passed" if get_decomposable_disjunction(ucnf1) is None else "Test 1 failed")
    print("Test 2 passed" if get_decomposable_disjunction(ucnf2) is not None else "Test 1 failed")


def get_decomposable_conjunction_test():
    ucnf1 = Disj([Conj([
        Disj([
            Tuple([Variable("x1")], "R"),
            Tuple([Variable("x1"), Variable("y2")], "S")
        ]),
        Disj([
            Tuple([Variable("x2")], "T"),
            Tuple([Variable("x2"), Variable("y2")], "S")
        ])
    ])])

    ucnf2 = Disj([Conj([
        Disj([
            Tuple([Variable("x1")], "R"),
            Tuple([Variable("x1"), Variable("y2")], "S")
        ]),
        Disj([
            Tuple([Variable("x2")], "T"),
            Tuple([Variable("x2"), Variable("y2")], "W")
        ])
    ])])
    print("Testing get_decomposable_conjunction_test")
    print("Test 1 passed" if get_decomposable_conjunction(ucnf1) is None else "Test 1 failed")
    # TODO: Need to test this better
    print("Test 2 passed kinda" if get_decomposable_conjunction(ucnf2) is not None else "Test 2 failed")

def perform_inclusion_exclusion_test():
    ucnf1 = Disj([
        Conj([
            Disj([
                Tuple([Variable("x1")], "R"),
                Tuple([Variable("x1"), Variable("y1")], "S")
            ])
        ]),
        Conj([
            Disj([
                Tuple([Variable("x2")], "T"),
                Tuple([Variable("x2"), Variable("y2")], "S")
            ])
        ])
    ])

    print("Testing perform_inclusion_exclusion_test")
    if perform_inclusion_exclusion(ucnf1).tostring() == "sum(+[(R(x1) || S(x1 , y1))] , -[(R(x1) || S(x1 , y1)) , (T(x2) || S(x2 , y2))] , +[(T(x2) || S(x2 , y2))])":
        print("Test 1 passed")

def get_unified_cnf_test():
    # TODO: It would be nice to make sure this works correctly with constants involved
    cnf1 = Conj([
        Disj([
            Tuple([Variable("x1")], "R"),
            Tuple([Variable("x1"), Variable("y1")], "S")
        ]),
        Disj([
            Tuple([Variable("x2")], "T"),
            Tuple([Variable("x2"), Variable("y2")], "S")
        ])
    ])

    print("Testing get_unified_cnf")
    test1 = get_unified_cnf(cnf1)
    print("Test 1 passed" if test1.tostring() == "[(R(x1) || S(x1 , y1)) , (T(x1) || S(x1 , y1))]" else "Test 1 failed")

def perform_cancellations_test():
    ucnf1 = Disj([
        Conj([
            Disj([
                Tuple([Variable("t", is_constant=True)], "R")
            ]),
            Disj([
                Tuple([Variable("t", is_constant=True)], "T")
            ])
        ]),
        Conj([
            Disj([
                Tuple([Variable("t", is_constant=True), Variable("y1")], "S")
            ]),
            Disj([
                Tuple([Variable("t", is_constant=True)], "R")
            ])
        ]),
        Conj([
            Disj([
                Tuple([Variable("t", is_constant=True), Variable("y2")], "S")
            ]),
            Disj([
                Tuple([Variable("t", is_constant=True)], "T")
            ])
        ]),
        Conj([
            Disj([
                Tuple([Variable("t", is_constant=True), Variable("y1")], "S")
            ]),
            Disj([
                Tuple([Variable("t", is_constant=True), Variable("y2")], "S")
            ]),
        ])
    ])

    print("Testing perform_cancellations")
    print(perform_cancellations(ucnf1).tostring())

# get_connected_components_test()
# convert_to_ucnf_test()
get_decomposable_disjunction_test()
get_decomposable_conjunction_test()
perform_inclusion_exclusion_test()
get_unified_cnf_test()
perform_cancellations_test()