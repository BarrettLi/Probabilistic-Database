from functools import reduce


class Variable:
    def __init__(self, name, is_constant=False):
        self.name = name
        # Specifies if the variable is quantified or is a constant
        self.is_constant = is_constant

    def getname(self):
        return self.name

    def setname(self, name):
        self.name = name

    def tostring(self):
        return self.name

    def setconstant(self, is_constant):
        self.is_constant = is_constant

    def getvariablenames(self):
        return {self.name}

    def getungroundedvariablenames(self):
        return {self.name} if not self.is_constant else set()

    def makecopy(self):
        return Variable(self.name, self.is_constant)

class Conj:
    """Represents a conjunction in FOL

    Attributes:
        items (list of Constant | Variable | Conj | Disj): list representing each item logically ANDed together
        negate (boolean, optional): indicates whether the conjunction is negated

    """
    def __init__(self, items, negate = False):
        self.items = items
        self.negate = negate

    def tostring(self):
        return "[{}]".format(' , '.join([item.tostring() for item in self.items]))

    def gettablenames(self):
        return reduce((lambda x, y: x | y), [set()] + [item.gettablenames() for item in self.items])

    def set_negation(self, negate):
        self.negate = negate

    def getvariablenames(self):
        return reduce((lambda x, y: x | y), [set()] + [item.getvariablenames() for item in self.items])

    def makecopy(self):
        return Conj([item.makecopy() for item in self.items], self.negate)

    def getungroundedvariablenames(self):
        return reduce((lambda x, y: x | y), [set()] + [item.getungroundedvariablenames() for item in self.items])

    def get_negated_query(self):
        return Disj([i.get_negated_query() for i in self.items], negate=self.negate)


class Disj:
    """Represents a disjunction in FOL

    Attributes:
        items (list of Constant | Variable | Conj | Disj): list representing each item logically ORed together
        negate (boolean, optional): indicates whether the disjunction is negated

    """
    def __init__(self, items, negate = False):
        self.items = items
        self.negate = negate

    def tostring(self):
        return "({})".format(' || '.join([item.tostring() for item in self.items]))

    def gettablenames(self):
        return reduce((lambda x, y: x | y), [set()] + [item.gettablenames() for item in self.items])

    def set_negation(self, negate):
        self.negate = negate

    def getvariablenames(self):
        return reduce((lambda x, y: x | y), [set()] + [item.getvariablenames() for item in self.items])

    def getungroundedvariablenames(self):
        return reduce((lambda x, y: x | y), [set()] + [item.getungroundedvariablenames() for item in self.items])

    def makecopy(self):
        return Disj([item.makecopy() for item in self.items], self.negate)

    def get_negated_query(self):
        return Conj([i.get_negated_query() for i in self.items], negate=self.negate)


# TODO: Product and PI tostring methods have not been tested and may be incorrect
class Product:
    """Represents a product

    Attributes:
        operands (list): list of operands of the product
        negate (boolean, optional): indicates whether the product is negated

    """

    def __init__(self, operands=None, negate=False):
        self.operands = operands if operands is not None else []
        self.negate = negate

    def tostring(self):
        res = "1 - " if self.negate else ""
        res += "prod({})".format(' , '.join([operand.tostring() for operand in self.operands]))
        return res

    def set_negation(self, negate):
        self.negate = negate

    def gettablenames(self):
        return reduce((lambda x, y: x | y), [set()] + [operand.gettablenames() for operand in self.operands])

    def accept(self, v):
        return v.visit_product(self)

class Sum:
    """Represents a sum

    Attributes:
        operands (list): list of (operand, pos) of the sum. pos == True if the operand is added, False if subtracted
        negate (boolean, optional): indicates whether the sum is negated

    """

    def __init__(self, operands=None, negate=False):
        self.operands = operands if operands is not None else []
        self.negate = negate

    # TODO: this doesn't work
    def tostring(self):
        res = "1 - " if self.negate else ""
        res += "sum({})".format(' , '.join([(('+' if operand[1] else '-') + operand[0].tostring()) for operand in self.operands]))
        return res

    def gettablenames(self):
        return reduce((lambda x, y: x | y), [set()] + [operand.gettablenames() for operand in self.operands])

    def accept(self, v):
        return v.visit_sum(self)

class Pi:
    """Represents a product quantified over some variable

    Attributes:
        variable (string):
        expression ():
        negate (boolean, optional): indicates whether the product is negated

    """

    def __init__(self, variable, expression, negate=False):
        self.variable = variable
        self.expression = expression
        self.negate = negate

    # Might be incorrect
    def tostring(self):
        res = ""
        if self.negate:
            res += "1 - "
        if isinstance(self.expression, list):
            res += "PI_{}({})".format(self.variable, ' , '.join([exp.tostring() for exp in self.expression]))
            return res

        res += "PI_{}({})".format(self.variable, self.expression.tostring())
        return res

    def gettablenames(self):
        return reduce((lambda x, y: x | y), [set()] + [exp.gettablenames() for exp in self.expression])

    def set_negation(self, negate):
        self.negate = negate

    def accept(self, v):
        return v.visit_pi(self)

class Tuple:
    """Represents a tuple in our probabilistic database

    Attributes:
        variables (list of Constant | Variable):
        tableName (string):
        negate (boolean, optional): indicates whether the tuple is negated

    """

    def __init__(self, variables, table_name, negate=False):
        self.variables = variables
        self.tableName = table_name
        self.negate = negate
        self.is_grounded = True

        for variable in variables:
            if not variable.is_constant:
                self.is_grounded = False
                break

    def tostring(self):
        return "{}({})".format(("~" if self.negate else "") + self.tableName, ' , '.join([variable.tostring() for variable in self.variables]))

    def gettablenames(self):
        return set(self.tableName)

    def recheckisgrounded(self):
        self.is_grounded = True

        for variable in self.variables:
            if not variable.is_constant:
                self.is_grounded = False
                break

    def isgrounded(self):
        return self.is_grounded

    def getvariablenames(self):
        return reduce((lambda x, y: x | y), [set()] + [variable.getvariablenames() for variable in self.variables])

    def getungroundedvariablenames(self):
        return reduce((lambda x, y: x | y), [set()] + [variable.getungroundedvariablenames() for variable in self.variables])

    def makecopy(self):
        return Tuple([variable.makecopy() for variable in self.variables], self.tableName, self.negate)

    def set_negation(self, negate):
        self.negate = negate

    def get_negated_query(self):
        return Tuple(variables=self.variables, table_name=self.tableName, negate=not self.negate)
    
    def accept(self,v):
        return v.visit_tuple(self)

