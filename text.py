def t(x, h=False):
    r = [[str(i)] for i in x] if not isinstance(x[0],list) else [list(map(str,row)) for row in x]
    w = [max(map(len,c)) for c in zip(*r)]
    return "\n".join("  ".join(f"{c:<{w[i]}}" for i,c in enumerate(row)) for row in r)

# Example – you can throw literally anything at it
my_list = ["Alice", 25, True]

print(t([7,8,9999]))