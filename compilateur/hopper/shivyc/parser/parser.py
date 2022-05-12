"""Entry point for the parser logic that converts a token list to an AST.

Each parse_* function corresponds to a unique non-terminal symbol in the C
grammar. It parses utils.tokens beginning at the given index to try to match
a grammar rule that generates the desired symbol. If a match is found,
it returns a tuple (Node, index) where Node is an AST node for that match
and index is one more than that of the last token consumed in that parse. If no
match is not found, raises an appropriate ParserError.

Whenever a call to a parse_* function raises a ParserError, the calling
function must either catch the exception and log it (using log_error),
or pass the exception on to the caller. A function takes the first approach
if there are other possible parse paths to consider, and the second approach if
the function cannot parse the entity from the tokens.

"""
import shivyc.parser.utils as p
import shivyc.tree.nodes as nodes

from shivyc.errors import error_collector
from shivyc.parser.utils import (add_range, log_error, ParserError,
                                 raise_error)
from shivyc.parser.declaration import parse_declaration, parse_func_definition

from pathlib import Path 

import json
import requests
import os
import sys
import subprocess

# Load env file
env = json.load(open('../env.json', 'r'))

def parse(tokens_to_parse, file, filename = None):
    """Parse the given tokens into an AST.

    Also, as the entry point for the parser, responsible for setting the
    tokens global variable.
    """
    p.best_error = None
    p.tokens = tokens_to_parse

    with log_error():
        ast =  parse_root(0,file, filename)[0]
        # save AST in a JSON file
        # if filename != None:
        #     with open(f'./{"out_ast" if filename == "" else filename}.json', 'w') as file:
        #         file.write('test')
        #         file.close()

        return ast    

    error_collector.add(p.best_error)
    return None
    
algo_args = ["free","ftree-loop-if-convert","fif-conversion","fdce","fforward-propagate","fexpensive-optimizations","floop-nest-optimize"]

def getgccargs(algo):
    global algo_args;
    res = ""
    for i in range(1,4):
        for row in range(0,len(algo)):
            if algo[row] == 1:
                res+= " -"+algo_args[i]
    return res


@add_range
def parse_root(index, file, filename = None):
    """Parse the given tokens into an AST."""
    items = []
    while True:
        with log_error():
            item, index = parse_func_definition(index)
            items.append(item)
            continue

        with log_error():
            item, index = parse_declaration(index)
            items.append(item)
            continue

        # If neither parse attempt above worked, break
        break

    # If there are tokens that remain unparsed, complain
    if not p.tokens[index:]:
        # ICI
        ast = nodes.Root(items)

        for el in str(ast).split('|'):
            if 'main' in el:
                # print(','.join(el.split(',')))
                tmp = el.split(',')
                tmp = list(filter(lambda a: a != "", tmp))
                
                for (i, el) in enumerate(tmp):
                    if el == 'OR':
                        tmp[i] = '||'

                ast_vec = {"ast_vec": tmp}

                key = None

                with open(os.path.expanduser('~/.hopper_key'), 'r') as f:
                    key = f.read()
                    f.close()
                    
                try:
                    model_res = requests.post(f'{env["API_URL"]}/api/model/exec', json={'api_key': key, 'ast': tmp})

                    if model_res.status_code == 200:
                        
                        command = f'gcc {file} -o {(Path(file).name)[:-2]}'
                        command += getgccargs(model_res.json());
                        subprocess.check_call(command.split(' '))
                        

                    elif model_res.status_code == 403:
                        print('Error with API KEY need to modify it (use --key option or edit ~/.hopper_key file by replacing the key in the file)')
                        sys.exit(0)

                except:
                    print('Connection issue, or service not available please check status')
                    sys.exit(0)

                # write astvec in a file
                # with open(f'./{"out_ast" if filename == "" else filename}.json', 'w') as file:
                #     file.write(json.dumps(ast_vec))
                #     file.close()
                

        # print('----')

        return nodes.Root(items), index
    else:
        raise_error("unexpected token", index, ParserError.AT)
