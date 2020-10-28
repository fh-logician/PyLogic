from typing import Union

from lark import Lark
from lark.tree import Tree as LarkTree

from expression import Expression
from variable import Variable
from quine_mccluskey import QM


class Tree:
    """A Logic Tree contains information relating to a logical expression,
    also known as a boolean algebra expression.

    :param expression: The logical expression to load into the Tree
    """

    BOOLEAN = Lark(
        """
        start: orexpr
        ?orexpr: (orexpr ("+" | "|" ~ 1..2 | "or" | "OR"))? andexpr
        ?andexpr: (andexpr ("*" | "&" ~ 1..2 | "and" | "AND"))? xorexpr
        ?xorexpr: (xorexpr ("^" | "xor" | "XOR"))? xnorexpr
        ?xnorexpr: (xnorexpr ("-^" | "xnor" | "XNOR"))? norexpr
        ?norexpr: (norexpr ("-+" | "nor" | "NOR"))? nandexpr
        ?nandexpr: (nandexpr ("-*" | "nand" | "NAND"))? term
        ?term: nexpr
            | pexpr
            | IDENT
        ?nexpr: TILDE orexpr
        ?pexpr: "(" orexpr ")"
            | "[" orexpr "]"
        TILDE: "~" | "!" | "not" | "NOT"

        %import common.CNAME -> IDENT
        %import common.WS
        %ignore WS
        """
    )

    @staticmethod
    def __create_dict(parse_tree):
        """Creates a parsable JSON object that can be parsed through LogicNode and LogicVar
        objects to be used to represent a boolean expression

        :param parse_tree: A Lark grammar tree object to parse through
        :returns: A tuple containing the parse expression and a list of variables in the expression
            The first entry in the tuple is the parsed expression
            The second entry in the tuple is a list of variables in the expression
        """

        variables = []

        # Check if the parse_tree is a LarkTree
        if isinstance(parse_tree, LarkTree):

            # Check if the expression is an orexpr (OR) or andexpr (AND)
            if parse_tree.data != "nexpr":

                # Get the left and right expression along with any new variables that may exist
                left, variables_new_left = Tree.__create_dict(parse_tree.children[0])
                right, variables_new_right = Tree.__create_dict(parse_tree.children[1])
                for variable in variables_new_left + variables_new_right:
                    if variable not in variables:
                        variables.append(variable)
                
                # Return the expression and the variables
                return {
                    "operator": parse_tree.data[ : parse_tree.data.find("expr")].upper(),
                    "left": left,
                    "right": right,
                    "has_not": False
                }, variables

            # Check if the expression is an nexpr (NOT)
            else:

                # Get the expression along with any new variables that may exist
                expression, variables_new = Tree.__create_dict(parse_tree.children[1])
                expression["has_not"] = not expression["has_not"]
                for variable in variables_new:
                    if variable not in variables:
                        variables.append(variable)
                
                # Return the expression and the variables
                return expression, variables

        # The parse_tree is an ident (Variable)
        return {
            "variable": parse_tree.value,
            "has_not": False
        }, [parse_tree.value]
    
    # # # # # # # # # # # # # # # # # # # #

    def __init__(self, expression: str):
        
        # Try to parse the expression
        try:
            expression, self.__variables = Tree.__create_dict(
                Tree.BOOLEAN.parse(expression).children[0] # This ignores the "start" Tree
            )
            self.__variables.sort()

            # Check if the expression is a LogicNode or LogicVar
            if "value" in expression:
                self.__root = Variable(json = expression)
            else:
                self.__root = Expression(json = expression)
        
        # If parsing the expression fails, the boolean expression is invalid
        except:
            raise ValueError("The expression given is invalid")
    
    def __str__(self) -> str:
        """Returns the string representation of this Tree"""
        return str(self.root)
    
    # # # # # # # # # # # # # # # # # # # #

    @property
    def root(self) -> Union[Expression, Variable]:
        """Returns the root of this Tree"""
        return self.__root
    
    @property
    def variables(self) -> list:
        """Returns the list of variables in this Tree"""
        return self.__variables
    
    # # # # # # # # # # # # # # # # # # # #

    def evaluate(self) -> bool:
        """Evaluates the root of this tree to get values for where the root
        evaluates to True and False (1 and 0)

        :returns: A list of evaluations and their truth values that make
            up the evaluation
        """
        
        # Iterate through all the integer values from 2 ** len(variables)
        evaluations = []
        for binary in range(2 ** len(self.variables)):

            # Create a dict for each variable and whether or not this variable
            #   is true at the current binary value
            truth_values = {}
            for i in range(len(self.variables)):
                key = self.variables[i]
                shift_amount = len(self.variables) - i - 1
                value = (binary & (1 << shift_amount)) != 0
                truth_values[key] = value

            # Add the evaluation for this binary value to the evaluations
            evaluations.append({
                "truth_values": truth_values,
                "truth_value": self.root.evaluate(truth_values)
            })
        return evaluations
    
    def get_table(self, *, as_list = False) -> Union[str, list]:
        """Creates a truth table out of the root node

        :param as_list: Whether or not to retrieve the table as 
            a list of rows
        
        :returns: A string containing the variables and where the root expression
            evaluates to True and False (1 and 0, respectively)
            or A list of rows for the truth table
        """

        # Create the header row
        #   which holds the variables and the result like the following:
        #   | a | b | c | (a * b) + c |
        header = "| {} | {} |".format(
            " | ".join(self.variables),
            str(self)
        )

        # Create the separator row
        #   which contains proper separation characters to create a more 
        #   tabular look like the following:
        #   +---+---+---+-------------+
        separator = "+-{}-+-{}-+".format(
            "-+-".join([
                "-" * len(variable)
                for variable in self.variables
            ]),
            "-" * len(str(self))
        )

        # Create the truth values and their evaluations
        #   which contains each boolean value and the final evaluation:
        #   | 0 | 1 | 0 |      0      |
        evaluations = self.evaluate()
        values = "\n".join([
            "| {} | {} |".format(
                " | ".join([
                    ("1" if evaluation["truth_values"][value] else "0").center(len(value))
                    for value in evaluation["truth_values"]
                ]),
                ("1" if evaluation["truth_value"] else "0").center(len(str(self)))
            )
            for evaluation in evaluations
        ])

        if as_list:
            return [
                header, separator, values
            ]
        return "{}\n{}\n{}".format(header, separator, values)

    def simplify(self, *, get_minterm=None) -> 'Tree':
        """Simplifies the boolean expression at the root
        and returns the most simplified expression obtained from either minterm or maxterm
        evaluation

        :param get_minterm: Whether or not to get the Minterm or Maxterm of this Tree
            By default, this will return the shortest one between the two.
        :returns: The simplifed boolean expression
        """

        # Get the minterm and maxterm true-at values
        #   Note that a minterm expression is true where the expression evaluates
        #   to True (1) and a maxterm expression is true where the expression evaluates
        #   to False (0)
        evaluations = self.evaluate()
        true_at_minterms = [
            decimal
            for decimal in range(len(evaluations))
            if evaluations[decimal]["truth_value"]
        ]
        true_at_maxterms = [
            decimal
            for decimal in range(len(evaluations))
            if not evaluations[decimal]["truth_value"]
        ]

        # Get the minterm and maxterm
        minterm_qm = QM(
            self.variables,
            true_at_minterms
        ).solve()

        maxterm_qm = QM(
            self.variables,
            true_at_maxterms,
            is_maxterm = True
        ).solve()

        # Either get the minterm or the maxterm
        #   if neither is specified, get the shortest one
        if get_minterm is not None:
            if get_minterm:
                return minterm_qm
            return maxterm_qm
        return min(minterm_qm, maxterm_qm, key = lambda qm: len(qm))
