from query import *
from Parser import Parser
from collections import defaultdict
from lifted_inference import *

class Visitor:
    def visit_product(self, produce):
        pass
    def visit_sum(self, sum):
        pass
    def visit_pi(self, pi):
        pass
    def visit_tuple(self, tuple):
        pass

class sqlVistor(Visitor):
    table_index = 0
    in_pi = False
    pi_variables = []
    def get_table_variables(self, node):
        variables = set()
        if isinstance(node, Tuple):
            return set([v.name[0] for v in node.variables])
        elif isinstance(node, Pi):
            return self.get_table_variables(node.expression)
        else:
            for op in node.operands:
                variables = variables | self.get_table_variables(op)
            return variables

    def get_common_variables(self, operands):
        table_variables = [self.get_table_variables(op) for op in operands]
        v_tables = defaultdict(set)
        for i in range(len(table_variables)):
            for j in range(i+1, len(table_variables)):
                common_variables = table_variables[i] & table_variables[j]
                if common_variables:
                    for v in common_variables:
                        v_tables[v].add("table" + str(self.table_index+i))
                        v_tables[v].add("table" + str(self.table_index+j))
        return v_tables

    def visit_product(self, product):
        if self.in_pi:
            # if Sum is in a Pi, then tables need to be joined properly
            tables = [op.accept(self) for op in product.operands]
            # get tables
            sub_queries = ["({}) AS table".format(tables[i]) + str(self.table_index+i) for i in range(len(tables))]
            # SELECT line
            sql_query = "SELECT {},1-".format(",".join(["table" + str(self.table_index) + "."+ v + " AS " + v for v in self.pi_variables])) if product.negate else "SELECT {},".format(",".join(["table" + str(self.table_index) + "."+ v + " AS " + v for v in self.pi_variables]))
            sql_query += "({}) AS p \nFROM {}\n".format("*".join(["(" + "table" + str(self.table_index+i) + ".p" + ")" for i in range(len(tables))]), ",".join(sub_queries))

            # get variables of each operands
            v_tables = self.get_common_variables(product.operands)
            if v_tables:
                where = []
                for x in v_tables:
                    table_list = list(v_tables[x])
                    for i in range(1, len(table_list)):
                        where.append("{}.{}={}.{}".format(table_list[0], x, table_list[i], x))
                sql_query += "WHERE {}".format(" AND ".join(where))

        else:
            # if Sum is not in a Pi, then it is simply a product among multiple numbers
            tables = [op.accept(self) for op in product.operands]
            # get tables
            sub_queries = ["({}) AS table".format(tables[i]) + str(self.table_index+i) for i in range(len(tables))]
            #  SELECT line
            sql_query = "SELECT 1-" if product.negate else "SELECT "
            sql_query += "({}) AS p \nFROM {}\n".format("*".join(["(" + ("-" if product.operands[i].negate else "") + "table" + str(self.table_index+i) + ".p" + ")" for i in range(len(tables))]), ",".join(sub_queries))
        self.table_index += len(tables)
        return sql_query

    def visit_sum(self, summation):
        operands = [op[0] for op in summation.operands]
        ops = [op[1] for op in summation.operands]
        if self.in_pi:
            # if Sum is in a Pi, then tables need to be joined properly
            tables = [op.accept(self) for op in operands]
            # get tables
            sub_queries = ["({}) AS table".format(tables[i]) + str(self.table_index+i) for i in range(len(tables))]
            # SELECT line
            sql_query = "SELECT {},1-".format(",".join(["table" + str(self.table_index) + "."+ v + " AS " + v for v in self.pi_variables])) if summation.negate else "SELECT {},".format(",".join(["table" + str(self.table_index) + "."+ v + " AS " + v for v in self.pi_variables]))
            sql_query += "({}) AS p \nFROM {}\n".format("+".join(["(" + ("+" if ops[i] else "-") + "table" + str(self.table_index+i) + ".p" + ")" for i in range(len(tables))]), ",".join(sub_queries))

            # get variables of each operands
            v_tables = self.get_common_variables(operands)
            if v_tables:
                where = []
                for x in v_tables:
                    table_list = list(v_tables[x])
                    for i in range(1, len(table_list)):
                        where.append("{}.{}={}.{}".format(table_list[0], x, table_list[i], x))
                sql_query += "WHERE {}".format(" AND ".join(where))

        else:
            # if Sum is not in a Pi, then it is simply a summation among multiple numbers
            tables = [op.accept(self) for op in operands]
            # get tables
            sub_queries = ["({}) AS table".format(tables[i]) + str(self.table_index+i) for i in range(len(tables))]
            #  SELECT line
            sql_query = "SELECT 1-" if summation.negate else "SELECT "
            sql_query += "({}) AS p \nFROM {}\n".format("+".join(["(" + ("+" if ops[i] else "-") + "table" + str(self.table_index+i) + ".p" + ")" for i in range(len(tables))]), ",".join(sub_queries))
        self.table_index += len(tables)
        return sql_query

    def visit_pi(self, pi):
        sql_query = ""
        if self.in_pi:
            # nest Pi
            self.pi_variables.append(pi.variable[0])
            tables = [pi.expression.accept(self)]
            # get tables
            sub_queries = ["({}) AS table".format(tables[i]) + str(self.table_index+i) for i in range(len(tables))]
            # SELECT line
            sql_query = "SELECT {},1-".format(",".join(["table" + str(self.table_index) + "."+ v for v in self.pi_variables[:-1]])) if pi.negate else "SELECT {},".format(",".join(["table" + str(self.table_index) + "."+ v for v in self.pi_variables[:-1]]))
            # aggregate PRODUCT
            sql_query += "EXP(SUM(LN({}))) AS p \nFROM \n{}\n".format("p", ",".join([s for s in sub_queries]))
            # group tuples by variables in higher level
            sql_query += "GROUP BY {}".format(",".join(self.pi_variables[:-1]))
            self.pi_variables = self.pi_variables[:-1]
        else:
            self.in_pi = True
            self.pi_variables.append(pi.variable[0])
            tables = [pi.expression.accept(self)]
            # get tables
            sub_queries = ["({}) AS table".format(tables[i]) + str(self.table_index+i) for i in range(len(tables))]
            # SELECT line
            sql_query = "SELECT 1-" if pi.negate else "SELECT "
            # aggregate PRODUCT
            sql_query += "EXP(SUM(LN({}))) AS p \nFROM \n{}\n".format("p", ",".join([s for s in sub_queries]))
            # change the state to not in a Pi
            self.in_pi = False
            # clean up the pi_variables
            self.pi_variables = []
        self.table_index += len(tables)
        return sql_query

    def visit_tuple(self, tuple):
        sql_query = ""
        if tuple.recheckisgrounded():
            # grounded atom, return certain tuple
            sql_query += "SELECT 1-p\n" if tuple.negate else "SELECT p\n"
            sql_query += "FROM {} \nWHERE {}".format(tuple.tableName.lower(), ' AND '.join([chr(ord('x') + i) + "=" + tuple.variables[i].tostring() for i in range(len(tuple.variables))]))
        else:
            # not grounded

            # keep track of duplicate variables within tuple
            varPrevIndex = {}
            dupVar = False
            vnames = [v.name[0] for v in tuple.variables]
            colToVar = []
            whereComponents = []
            for i in range(len(vnames)):
                if vnames[i] in varPrevIndex:
                    dupVar = True
                    colToVar.append("col{}".format(i))
                    prevIndex = varPrevIndex[vnames[i]]
                    whereComponents.append("col{} = col{}".format(prevIndex,i))
                else:
                    colToVar.append("col{} AS {}".format(i, vnames[i]))
                varPrevIndex[vnames[i]] = i

            whereClause = " WHERE " + " AND ".join(whereComponents) if dupVar else ""

            sql_query += "SELECT {},p FROM {}".format(','.join(colToVar), tuple.tableName.lower()) if not tuple.negate else "SELECT {},1-p AS p FROM {}".format(','.join(colToVar), tuple.tableName.lower())
            sql_query += whereClause
        return sql_query

# parser = Parser()
# # parser.connect()
# # parser.parse()
# parser.parseQuery("query2.txt")
# v = sqlVistor()
# print(perform_inference_dnf(parser.queries[0]).tostring())
# print(perform_inference_dnf(parser.queries[0]).accept(v))
# print(atom2sql(perform_inference_dnf(parser.queries[0])))
# testcase0 = Sum([Sum([Tuple([Variable("x1")],"r")]), Tuple([Variable("x"), Variable("y")],"q")],True)
# testcase1 = Pi("x",Tuple([Variable("x")], "r"))
# testcase2 = Pi("x", Pi("y", Tuple([Variable("x"), Variable("y")], "r"), negate=True))
# testcase3 = Pi("x", Pi("y", Pi("z", Tuple([Variable("x"), Variable("y"), Variable("z")], "r"))))
# testcase4 = Tuple([Variable("0", is_constant=True), Variable("2", is_constant=True)], "r")
# testcase5 = Sum(
#     [ Tuple([Variable("x")], "p"),
#       Tuple([Variable("x"), Variable("y")], "q"),
#       Tuple([Variable("x"), Variable("y")],"r")]).operands
# testcase6 = Pi("x", Pi("y", Product([Tuple([Variable("x"), Variable("y")], "r"), Tuple([Variable("x")], "q")])))
# print(testcase6.accept(v))
