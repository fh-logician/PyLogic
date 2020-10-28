class LogicVar:
    """A LogicVar class holds information about a variable, or a literal, in a boolean algebraic
    expression of logical expression.

    Parameters
    ----------
        value : str
            The variable letter for this LogicVar object
        has_not : boolean
            Whether or not this LogicVar object has a ~ (NOT) operator attached to it
    
    Keyword Parameters
    ------------------
        json : dict
            A JSON object to load a LogicVar object from.
                The required keys are the same as the parameters (value, has_not)
    """

    def __init__(self, value = None, has_not = None, *, json = None):

        # Check if the JSON object is given
        if json is not None:

            # Validate that value and has_not keys are given
            if "value" in json and "has_not" in json:
                value = json["value"]
                has_not = json["has_not"]
            else:
                raise KeyError("The \"value\" and \"has_not\" keys must exist in the LogicVar JSON.")
        
        # Make sure value and has_not exist
        if value is not None and has_not is not None:
            self.__value = value
            self.__has_not = has_not
        else:
            raise ValueError("The \"value\" and \"has_not\" parameters must not be a NoneType.")
    
    def __str__(self):
        return "{}{}".format(
            "NOT " if self.has_not() else "",
            self.get_value()
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_value(self):
        """Returns the variable letter of this LogicVar object

        Returns
        -------
            str
        """
        return self.__value
    
    def has_not(self):
        """Returns whether or not this LogicVar object has a ~ (NOT) operator attached to it

        Returns
        -------
            boolean
        """
        return self.__has_not
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Evaluation Methods
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def evaluate(self, truth_values):
        """Evaluates this LogicVar object given a dict of truth values that include the letter

        Parameters
        ----------
            truth_values : dict
                A JSON object of truth values for this LogicVar object to use
                to evaluate.

        Returns
        -------
            boolean
                The boolean evaluation of this LogicVar object
        """
        if self.has_not():
            return not truth_values[self.get_value()]
        return truth_values[self.get_value()]