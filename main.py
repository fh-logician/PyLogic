from expression import Expression
from variable import Variable
from tree import Tree

# # # # #
 
a = Variable("a")  # This is the basic form of a Variable
b = Variable("b", has_not=True)  # This will attach a NOT operator to this Variable
 
print(a)  # --> "a"
print(b)  # --> "not(b)"

# # # # #
 
expr = Expression(
    Expression.OR,  # You can use either the Expression.OR, or just type "or"
    a, b            # Then you can specify the left and right, respectively
)                   # Optionally, just like Variable, you can specify the has_not operator
 
expr1 = Expression(
    Expression.OR,
    Variable("a"),
    Variable("b", has_not=True)
)

print(expr)
print(expr1)

# # # # #

a = {
    "variable": "a",
}
 
b = {
    "variable": "b",
    "has_not": True
}
 
expr = {
    "operator": "or",
    "left": a,
    "right": b
}
 
nested = {
    "operator": "or",
    "left": {
        "operator": "or",
        "left": {
            "variable": "a"
        },
        "right": {
            "variable": "b",
            "has_not": True
        }
    },
    "right": {
        "variable": "c",
        "has_not": True
    },
    "has_not": True
}

var_a = Variable(json = a)
var_b = Variable(json = b)

expr_expr = Expression(json = expr)
expr_nested = Expression(json = nested)

print(var_a)  # --> a
print(var_b)  # --> NOT b

print(expr_expr)  # --> a OR NOT b
print(expr_nested)  # --> NOT ((a OR NOT b) or NOT c)

# # # # #
 
expr = Tree("a or b")  # This will set the root of the Tree to an Expression
expr1 = Tree("not a")  # This will set it to a Variable

print(type(expr.root))  # --> Expression
print(type(expr1.root))  # --> Variable

# # # # #

a = Tree("a and b or a and c")
b = Tree("a and (b or c)")

print(a.get_table())
print(b.get_table())

print(str(a.simplify()))
print(str(b.simplify()))