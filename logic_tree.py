from lark import Lark
from lark.tree import Tree
from logic_node import LogicNode
from logic_var import LogicVar
from quine_mccluskey import QM

class LogicTree:
    """A LogicTree class contains the root of a Boolean Expression
    and evaluates the expression or creates a truth table out of the expression

    Parameters
    ----------
        expression : str
            The expression for this LogicTree
    
    Raises
    ------
        ValueError
            When the expression is invalid due to invalid operator chaining (+ +), missing
            parenthesis, or variable of length > 1
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

        Parameters
        ----------
            parse_tree : Tree
                A Lark grammar tree object to parse through
        
        Returns
        -------
            dict, list : tuple
                A tuple containing the parsed expression and a list of variables in the expression
        """

        variables = []

        # Check if the parse_tree is a Tree
        if isinstance(parse_tree, Tree):

            # Check if the expression is an orexpr (OR) or andexpr (AND)
            if parse_tree.data != "nexpr":

                # Get the left and right expression along with any new variables that may exist
                left, variables_new_left = LogicTree.__create_dict(parse_tree.children[0])
                right, variables_new_right = LogicTree.__create_dict(parse_tree.children[1])
                for variable in variables_new_left + variables_new_right:
                    if variable not in variables:
                        variables.append(variable)
                
                # Return the expression and the variables
                return {
                    "left": left,
                    "operator": parse_tree.data[ : parse_tree.data.find("expr")].upper(),
                    "right": right,
                    "has_not": False
                }, variables

            # Check if the expression is an nexpr (NOT)
            else:

                # Get the expression along with any new variables that may exist
                expression, variables_new = LogicTree.__create_dict(parse_tree.children[1])
                expression["has_not"] = not expression["has_not"]
                for variable in variables_new:
                    if variable not in variables:
                        variables.append(variable)
                
                # Return the expression and the variables
                return expression, variables

        # The parse_tree is an ident (Variable)
        return {
            "value": parse_tree.value,
            "has_not": False
        }, [parse_tree.value]

    def __init__(self, expression):

        # Try to parse the expression
        try:
            self.expression, self.variables = LogicTree.__create_dict(
                LogicTree.BOOLEAN.parse(expression).children[0] # This ignores the "start" Tree
            )
            self.variables.sort()

            # Check if the expression is a LogicNode or LogicVar
            if "value" in self.expression:
                self.root = LogicVar(json = self.expression)
            else:
                self.root = LogicNode(json = self.expression)
        
        # If parsing the expression fails, the boolean expression is invalid
        except:
            raise ValueError("The expression given is invalid")
    
    def __str__(self):
        return str(self.root)

    def evaluate(self):
        """Evaluates the root of this tree to get values for where the root
        evaluates to True and False (1 and 0)

        Returns
        -------
            list
                A list of evaluations and their truth values that make up the 
                evaluation
        """
        
        # Iterate through all the integer values from 2 ** len(variables)
        evaluations = []
        for binary in range(2 ** len(self.variables)):

            # Create a dict for each variable and whether or not this variable
            #   is true at the current binary value
            truth_values = {
                self.variables[i]: binary & (1 << (len(self.variables) - 1 - i)) != 0
                for i in range(len(self.variables))
            }

            # Add the evaluation for this binary value to the evaluations
            evaluations.append({
                "truth_values": truth_values,
                "truth_value": self.root.evaluate(truth_values)
            })
        return evaluations
    
    def get_table(self, as_list = False):
        """Creates a truth table out of the root node

        Returns
        -------
            str
                A string containing the variables and where the root expression
                evaluations to True and False (1 and 0)
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
    
    def simplify(self, get_minterm = None):
        """Simplifies the boolean expression at the root
        and returns the most simplified expression obtained from either minterm or maxterm
        evaluation

        Parameters
        ----------
            get_minterm : boolean
                Whether to get the minterm expression or the maxterm expression
                Note that if this is None, the shortest expression will be given between
                    the minterm and maxterm expression

        Returns
        -------
            LogicTree
                The simplified boolean expression
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

        minterm_qm = QM(
            self.variables,
            true_at_minterms
        ).get_function()

        maxterm_qm = QM(
            self.variables,
            true_at_maxterms,
            is_maxterm = True
        ).get_function()

        if get_minterm is not None:
            if get_minterm:
                return minterm_qm
            return maxterm_qm
        return min(minterm_qm, maxterm_qm, key = lambda qm: len(qm))