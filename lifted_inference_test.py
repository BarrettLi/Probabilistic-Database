from lifted_inference import *
from Parser import *

def perform_inference_test():
    cnf1 = Conj([
            Disj([
                Tuple([Variable("x"), Variable("y")], "R", negate=True),
                Tuple([Variable("x")], "Q", negate=True)
            ])
        ])

    cnf2 = Conj([
            Disj([
                Tuple([Variable("x"), Variable("y")], "R", negate=True),
                Tuple([Variable("x"), Variable("y")], "Q", negate=True)
            ])
        ])

    print("Testing the lifted inference algorithm")
    # print(perform_inference(cnf1).tostring())
    print(perform_inference(cnf2).tostring())

def perform_inference_dnf_test():
    dnf1 = Disj([
            Conj([
                Tuple([Variable("x"), Variable("y")], "R"),
                Tuple([Variable("x")], "Q")
            ])
        ])

    dnf2 = Disj([
        Conj([
            Tuple([Variable("x1"), Variable("y1")], "R"),
            Tuple([Variable("x1")], "P"),
            Tuple([Variable("x2"), Variable("y2")], "R"),
            Tuple([Variable("x2")], "Q")
        ])
    ])

    print("Testing the lifted inference algorithm, dnf version")
    print("Test 1 passed" if perform_inference_dnf(dnf1).tostring() == "1 - PI_x(1 - prod(Q(x) , 1 - PI_y(~R(x , y))))" else "Test 1 failed")
    print("Test 2 passed" if perform_inference_dnf(dnf2).tostring() == "1 - sum(+PI_x1(1 - prod(P(x1) , 1 - PI_y1(~R(x1 , y1)))) , -PI_x1(1 - prod(1 - PI_y1(~R(x1 , y1)) , 1 - prod(~Q(x1) , ~P(x1)))) , +PI_x2(1 - prod(Q(x2) , 1 - PI_y2(~R(x2 , y2)))))" else "Test 2 failed")
    parser = Parser()
    parser.parseQuery("query1.txt")
    print(perform_inference_dnf(parser.queries[0]).tostring())

# perform_inference_test()
perform_inference_dnf_test()