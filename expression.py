from typing import Union
from variable import Variable


class Expression:
    """A Logic Expression contains information that pertains to
    the logical operator, the left and right sides of this Expression,
    and whether or not this Expression has a NOT variable attached to it

    :param operator: The logical operator for this Expression
    :param left: The left side of this Expression
    :param right: The right side of this Expression
    :param has_not: Whether or not this Expression has a NOT variable
        attached to it
    :param json: A dictionary to load this Expression with
        Note: The "operator", "left", and "right" keys must exist
    """

    def __init__(self, operator: str=None, 
                        left: Union['Expression', Variable]=None, 
                        right: Union['Expression', Variable]=None, 
                        has_not: bool=False, *,
                        json: dict=None):
        
        # Check if the json is given
        if json is not None:
            if "operator" not in json and "left" not in json and "right" not in json:
                raise KeyError("Operator, left, and right keys must exist")
            
            operator = json["operator"]
            has_not = json.get("has_not", False)

            if "variable" in json["left"]:
                left = Variable(json = json["left"])
            else:
                left = Expression(json = json["left"])
            
            if "variable" in json["right"]:
                right = Variable(json = json["right"])
            else:
                right = Expression(json = json["right"])
        
        self.__operator = operator
        self.__left = left
        self.__right = right
        self.__has_not = has_not
    
    # # # # # # # # # # # # # # # # # # # #

    @property
    def operator(self) -> str:
        """Returns the logical operator of this Expression"""
        return self.__operator
    
    @property
    def left(self) -> ['Expression', Variable]:
        """Returns the left side of this Expression"""
        return self.__left
    
    @property
    def right(self) -> ['Expression', Variable]:
        """Returns the right side of this Expression"""
        return self.__right
    
    @property
    def has_not(self) -> bool:
        """Returns whether or not this Expression has a NOT
        operator attached to it
        """
        return self.__has_not
    
    # # # # # # # # # # # # # # # # # # # #

    def functional(self) -> str:
        """Returns a functional representation of this Expression

        For example:
         * `a or b` <=> `or(a, b)`
         * `not a or b` <=> `or(not(a), b)`
         * `not(a or b)` <=> `not(or(a, b))`
        """
        if self.has_not:
            return f"not({self.operator}({self.left.functional()}, {self.right.functional()}))"
        return f"{self.operator}({self.left.functional()}, {self.right.functional()})"
    
    def evaluate(self, truth_values: dict) -> bool:
        """Evaluates this Expression given a dict of truth values
        to evaluate it with.

        For example, if the given truth value is:

            {
                "a": True,
                "b": False
            }
        
        and this Expression is `not a or b`, then the expression 
        would be False since `a` is True

        :param truth_values: The truth values given to determine the boolean
            value of this Expression
        """
        left = self.left.evaluate(truth_values)
        right = self.right.evaluate(truth_values)

        # Evaluate the left and right sides of this Expression
        evaluation = False
        if self.operator == "OR":
            evaluation = left or right
        elif self.operator == "NOR":
            evaluation = not(left or right)
        elif self.operator == "AND":
            evaluation = left and right
        elif self.operator == "NAND":
            evaluation = not(left and right)
        elif self.operator == "XOR":
            evaluation = left ^ right
        elif self.operator == "XNOR":
            evaluation = not(left ^ right)
        
        # Handle the NOT operator if there is one
        return self.has_not ^ evaluation