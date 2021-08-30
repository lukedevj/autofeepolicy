from os import popen, makedirs, system
from json import loads
from os.path import exists, expanduser

def percentage(x: int, y: int) -> int:
    if not isinstance(x, (int, float)):
        raise ValueError(
            'Input values should be a number, your first input is a %s' % type(x))

    if not isinstance(y, (int, float)):
        raise ValueError(
            'Input values should be a number, your second input is a %s' % type(y))
    
    try:
        p = (x / float(y))
        return  (p * 100)
    except ZeroDivisionError:
        raise Exception('ZeroDivisionError: division by zero')
    
def shell(command: str) -> str:
    return popen(command).read()

def which(name: str) -> str:
    return shell(f'which {name}')[:-1]

def touchdir(path: str) -> str:
    path = expanduser(path)
    makedirs(path, exist_ok=True)
    return path

def touchfile(path: str) -> str:
    path = expanduser(path)
    if exists(path) == False:
        with open(path, 'w') as file:
            file.write('')
    return path 

def updatepolicyfee(**kwargs: dict) -> str:
    command = '/usr/local/bin/bos fees'
    if not (command):
        raise Exception('Balance of Satoshi is not installed.')
    
    command+= (
        f' --node {kwargs.get("node")}' if kwargs.get('node') else ''
    )
    command+= (
        f' --set-fee-rate={kwargs.get("formula")}' \
            if kwargs.get('formula') else ''
    )
    command+= (
        f' --to {kwargs.get("to")}' if kwargs.get('to') else ''
    )
    execute = shell(command)
    if not ('Peer' in execute):
        raise Exception(execute)
    return True
