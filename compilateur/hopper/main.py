"""Main executable for ShivyC compiler."""

import argparse
import pathlib
import platform
import subprocess
import sys

import shivyc.lexer as lexer
import shivyc.preproc as preproc

from shivyc.errors import error_collector, CompilerError
from shivyc.parser.parser import parse

from shivyc.env import env

import os

global debug

def main():
    """Run the main compiler script."""

    if platform.system() != "Linux":
        err = "only x86_64 Linux is supported"
        print(CompilerError(err))
        return 1

    arguments = get_arguments()
    env.set_debug(arguments.debug if arguments.debug else 0)

    # API key stored Here
    key = arguments.key
    
    if key == None:
        if os.path.isfile(os.path.expanduser('~/.hopper_key')) == False:
            print('Dont have api key information (Key file or --key option)')
            sys.exit(0)

        else:
            with open(os.path.expanduser('~/.hopper_key'), 'r') as f:
                key = f.read()
                f.close()

    elif key != None:
        with open(os.path.expanduser('~/.hopper_key'), 'w') as f:
            f.write(key)
            f.close()
        # if os.path.isfile(os.path.expanduser('~/.hopper_key')) == False:
        #     with open(os.path.expanduser('~/.hopper_key'), 'w') as f:
        #         f.write(key)
        #         f.close()

    objs = []
    for file in arguments.files:
        # process the file
        tmp = process_file(file, arguments)

        if tmp:
            # default out file name
            filename = f'out_{arguments.files.index(file)}'
            
            # check if we give name in the --out parameters
            if arguments.out != None:
                try:
                    # bind gived name if exist else that take defuault's one
                    filename = arguments.out[arguments.files.index(file)]
                except:
                    print(f'Missing executable name for {file} and will be named : out_{arguments.files.index(file)}')
                    filename = f'out_{arguments.files.index(file)}'

        # objs.append(process_file(file, arguments))
        objs.append(tmp)

    error_collector.show()

def process_file(file, args):
    """Process single file into object file and return the object file name."""
    if file[-2:] == ".c":
        return process_c_file(file, args)
    elif file[-2:] == ".o":
        return file
    else:
        err = f"unknown file type: '{file}'"
        error_collector.add(CompilerError(err))
        return None


def process_c_file(file, args):
    """Compile a C file into an object file and return the object file name."""
    code = read_file(file)
    if not error_collector.ok():
        return None
    
    if args.debug:
        token_list = lexer.tokenize(code, file)
    
    else:
        token_list = lexer.tokenize(code, file)
    
    if not error_collector.ok():
        return None

    token_list = preproc.process(token_list, file)
    if not error_collector.ok():
        return None

    # If parse() can salvage the input into a parse tree, it may emit an
    # ast_root even when there are errors saved to the error_collector. In this
    # case, we still want to continue the compiler stages.

    # check if we give the --ast arguments
    if args.ast != None:
        # check if we need to give the default value or the custom name
        if args.ast != '':
            ast_root = parse(token_list,file, f'{args.ast}')
        
        elif args.ast == '' or len(args.ast) - 1 < args.files.index(file):
            ast_root = parse(token_list,file, f'out_ast')
    
    else:
        ast_root = parse(token_list,file)

    if not ast_root:
        return None

def get_arguments():
    """Get the command-line arguments.

    This function sets up the argument parser. Returns a tuple containing
    an object storing the argument values and a list of the file names
    provided on command line.
    """
    desc = """Compile, assemble, and link C files. Option flags starting
    with `-z` are primarily for debugging or diagnostic purposes."""
    parser = argparse.ArgumentParser(
        description=desc, usage="shivyc [-h] [options] files...")

    # Files to compile
    parser.add_argument("files", metavar="files", nargs="+")
    # --out filesname
    # ex: shivyc example.c ex.c --out 1 2
    parser.add_argument("--out", metavar="out", nargs="+")

    # --ast filename (default filename will be out_ast.json)
    parser.add_argument("--ast", metavar="ast", nargs="?", const='')
    parser.add_argument("--key", metavar="key", nargs="?", const='')

    parser.add_argument("-debug")

    # Boolean flag for whether to print register allocator performance info
    parser.add_argument("-z-reg-alloc-perf",
                        help="display register allocator performance info",
                        dest="show_reg_alloc_perf", action="store_true")
    
    return parser.parse_args()


def read_file(file):
    """Return the contents of the given file."""
    try:
        with open(file) as c_file:
            return c_file.read()
    except IOError as e:
        descrip = f"could not read file: '{file}'"
        error_collector.add(CompilerError(descrip))

if __name__ == "__main__":
    sys.exit(main())
