from lark import Lark
from lark.tree import Tree as LarkTree

from expression import Expression
from variable import Variable


class Tree:
    """A Logic Tree contains information relating 
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

    def __init__(self, expression: str):
        pass
    
    