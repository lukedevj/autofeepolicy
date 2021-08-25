def loads(data: str) -> dict:
    d, c, k = data.replace(' ', ''), dict(), None
    for x in d.split():
        if (x[0] == '[') and (x[-1] == ']'):
            k = (x[1:-1])
            if not (k in c.keys()):
                c[k] = dict()
        else:
            x = x.split('=')
            if '#' in x[0]: continue
            x[1] = x[1].replace('\'', '')
            if (len(x) >= 2) and (x[0][0] != '#'):
                x = iter(x)
                y = zip(x, x)
                if (k != None):
                    c[k].update(dict(y))
                else:
                    c.update(dict(y))
    return (c)

def load(file: str) -> dict:
    with open(file, 'r') as f:
        return loads(f.read())
