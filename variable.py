class Variable:
    """A Logic Variable contains information that pertains to
    the letter of a value and whether or not there is a NOT
    operator attached to it.

    :param variable: The letter or word for this Variable
    :param has_not: Whether or not this Variable has a NOT operator
        attached to it
    :param json: A dictionary to load the Variable with
        Note: The "variable" key must exist
    :raises AttributeError: When the `variable` key does not exist in the json
    """

    def __init__(self, variable: str=None, has_not: bool=False, *, json: dict=None):

        # Check if the json is given
        if json is not None:
            if "variable" not in json:
                raise AttributeError("Variable key must exist in json")
            
            variable = json["variable"]
            has_not = json.get("has_not", False)
        
        # Set this Variable's fields
        self.__variable = variable
        self.__has_not = has_not
    
    def __str__(self) -> str:
        """Returns the string representation of this Variable"""
        if self.has_not:
            return f"NOT {self.variable}"
        return self.variable
    
    # # # # # # # # # # # # # # # # # # # #

    @property
    def variable(self) -> str:
        """Returns the string variable of this Variable"""
        return self.__variable
    
    @property
    def has_not(self) -> bool:
        """Returns whether or not this Variable has a NOT
        operator attached to it
        """
        return self.__has_not
    
    # # # # # # # # # # # # # # # # # # # #

    def functional(self) -> str:
        """Returns a functional representation of this Variable

        For example:
         * `not a` <=> `not(a)`
        """
        if self.has_not:
            return f"not({self.variable})"
        return self.variable

    def evaluate(self, truth_values: dict) -> bool:
        """Evaluates this Variable given a dict of truth values
        to evaluate it with.

        For example, if the given truth values is:
        
            {
                "a": True,
                "b": False
            }
        
        and this Variable is `not a` then the evaluation 
        would be False since `a` is True

        :param truth_values: The truth values given to determine the boolean
            value of this Variable
        """
        if self.variable not in truth_values:
            raise KeyError(f"No variable \"{self.variable}\" was found in truth values")
        
        # XOR the truth value and whether this Variable has a has not
        #   because that will return the proper evaluation
        return truth_values[self.variable] ^ self.has_not
