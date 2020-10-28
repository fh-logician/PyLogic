from logic_var import LogicVar

class LogicNode:
    """A LogicNode class holds information about a boolean expression

    Parameters
    ----------
        left : LogicNode or LogicVar
            The left side of this LogicNode expression
        operator : enum.OPERATOR
            The operator of this LogicNode expression
        right : LogicNode or LogicVar
            The right side of this LogicNode expression
        has_not : boolean
            Whether or not this LogicNode object has a ~ (NOT) operator attached to it (Defaults to False)
    
    Keyword Parameters
    ------------------
        json : dict
            A JSON object to load a LogicNode object from.
                The required keys are the same as the parameters (left, operator, right, has_not)
    """

    def __init__(self, left = None, operator = None, right = None, has_not = False, *, json = None):

        # Check if the JSON object is given
        if json is not None:
            
            # Validate that the left, operator, right, and has_not keys exist
            if "left" in json and "operator" in json and "right" in json and "has_not" in json:

                # Check if the operator is a NAND, a NOR, or an XNOR, invert the has_not
                operator = json["operator"]
                has_not = json["has_not"]
                if operator in ["NAND", "NOR", "XNOR"]:
                    has_not = not has_not
                
                left = LogicNode(json = json["left"]) if "value" not in json["left"] else LogicVar(json = json["left"])
                right = LogicNode(json = json["right"]) if "value" not in json["right"] else LogicVar(json = json["right"])
            
            # The left, operator, right, and has_not keys do not exist
            else:
                raise KeyError("The \"left\", \"operator\", \"right\", and \"has_not\" keys must exist in the LogicNode JSON")
        
        # Make sure left, operator, right, and has_not exist
        if left is not None and operator is not None and right is not None and has_not is not None:
            self.__left = left
            self.__operator = operator
            self.__right = right
            self.__has_not = has_not
        else:
            raise ValueError("The \"left\", \"operator\", \"right\", and \"has_not\" parameters must not be a NoneType.")
    
    def __str__(self):
        if not self.has_not():
            return "{} {} {}".format(
                str(self.get_left()), self.get_operator(), str(self.get_right())
            )
        return "NOT({} {} {})".format(
            str(self.get_left()), self.get_operator(), str(self.get_right())
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_left(self):
        """Returns the left value of this LogicNode object

        Returns
        -------
            LogicNode or LogicVar
        """
        return self.__left
    
    def get_operator(self):
        """Returns the operator of this LogicNode object

        Returns
        -------
            str
        """
        return self.__operator
    
    def get_right(self):
        """Returns the right value of this LogicNode object

        Returns
        -------
            LogicNode or LogicVar
        """
        return self.__right
    
    def has_not(self):
        """Returns whether or not this LogicNode object has a ~ (NOT) operator attached to it

        Returns
        -------
            boolean
        """
        return self.__has_not

    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Evaluation Methods
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def evaluate(self, truth_values):
        """Evaluates this LogicNode object given a dict of truth values

        Parameters
        ----------
            truth_values : dict
                A JSON object of truth values for this LogicNode object to use
                to evaluate.

        Returns
        -------
            boolean
                The boolean evaluation of this LogicNode object
        """
        left = self.get_left().evaluate(truth_values)
        right = self.get_right().evaluate(truth_values)

        if self.get_operator() == "OR":
            evaluation = left or right
        elif self.get_operator() == "AND":
            evaluation = left and right
        
        if self.has_not():
            return not evaluation
        return evaluation
    
    def functional(self) -> str:
        """Returns a functional representation of this Expression

        For example:
            - ``a AND b`` would be functionally equivalent to ``and(a, b)``
            - ``NOT a AND b`` would be functionally equivalent to ``and(not(a), b)``
            - ``NOT (a AND b)`` would be functionally equivalent to ``not(and(a, b))``
        """
        expr = f"{self.get_operator().lower()}({self.get_left().functional()}, {self.get_right().functional()})"
        if self.has_not():
            expr = f"not({expr})"
        return expr