# PyLogic

PyLogic is a Python-based Boolean Expression evaluator

### Variable

A `Variable` is what is used to hold a boolean value in a boolean expression.

To create a Variable:
```python
from variable import Variable

a = Variable("a")  # This is the basic form of a Variable
b = Variable("b", has_not=True)  # This will attach a NOT operator to this Variable

print(a)  # --> "a"
print(b)  # --> "not(b)"
```

As you can see, the `has_not` key is `False` by default so there is no need to set it
if the Variable does not have a NOT operator attached to it.

### Expression

An `Expression` is what is used to actually hold a Boolean Expression
To create an Expression:
```python
from expression import Expression
from variable import Variable

a = Variable("a")
b = Variable("b", has_not=True)

expr = Expression(
    Expression.OR,  # You can use either the Expression.OR, or just type "or"
    a, b            # Then you can specify the left and right, respectively
)                   # Optionally, just like Variable, you can specify the has_not operator

expr1 = Expression(
    Expression.OR,
    Variable("a"),
    Variable("b", has_not=True)
)
```

As you can see in `expr1`, you can also create the objects within the Expression object
that you are creating.

#### Using JSON

It is also possible to use a JSON dictionary to create a Variable or an Expression.

The format will be the same as the Variable and Expression objects.

For example:
```python
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
```

You can see above that you can nest as many expressions as you want.

To load them into the Expression and Variable, you must use the `json` variable in 
their respective objects to instantiate it

### Tree

The `Tree` object is what is used to actually evaluate and create a truth table from the root of the `Tree`.

The root of a `Tree` object can either be an `Expression` or a `Variable`, it all depends on the expression
entered in the `Tree`.

For example:
```python
from tree import Tree

expr = Tree("a or b")  # This will set the root of the Tree to an Expression
expr1 = Tree("not a")  # This will set it to a Variable
```

## Using Quine-McCluskey

The Quine-McCluskey algorithm is built into this so there is no need to depend on other Quine-McCluskey
packages to use in PyLogic.

To use it, you just need to call the `simplify` method which will return a new `Tree` object of the
simplified expression.

For example, the boolean expression `(a or b) and (a or c)` which can be simplified
to `a or (b and c)`
```python
expr = Expression(
    Expression.AND,
    Expression(
        Expression.OR,
        Variable("a"),
        Variable("b")
    ),
    Expression(
        Expression.OR,
        Variable("a"),
        Variable("c")
    )
)

expr_simplified = expr.simplify()  # This will return a tree that is
                              # equivalent to the following

expr1 = Expression(
    Expression.OR,
    Variable("a"),
    Expression(
        Expression.AND,
        Variable("b"),
        Variable("c")
    )
)
```