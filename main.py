from tree import Tree

a = Tree("(a or b) and (a or c)")
print(a.simplify())