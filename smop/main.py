# SMOP -- Simple Matlab/Octave to Python compiler
# Copyright 2011-2016 Victor Leikehman

from __future__ import print_function

import py_compile
import tempfile
import fnmatch
import tarfile
import sys
import os
import traceback
from os.path import basename, splitext

sys.argv.append('temp/stripcell.m')
sys.argv.append('-o')
sys.argv.append('temp/stripcell.py')
#sys.argv.append('-H')
#sys.argv.append('-P')

import options
import parse
import resolve
import backend
import version

def print_header(fp):
    if options.no_header:
        return
    print("import numpy as np", file=fp)
    print("import re", file=fp)

def main():
    if "M" in options.debug:
        import pdb
        pdb.set_trace()
    if not options.filelist:
        options.parser.print_help()
        return
    if options.output == "-":
        fp = sys.stdout
    elif options.output:
        fp = open(options.output, "w")
    else:
        fp = None
    if fp:
        print_header(fp)

    nerrors = 0
    for i, options.filename in enumerate(options.filelist):
        try:
            if options.verbose:
                print(i, options.filename)
            if not options.filename.endswith(".m"):
                print("\tIgnored: '%s' (unexpected file type)" %
                      options.filename)
                continue
            if basename(options.filename) in options.xfiles:
                if options.verbose:
                    print("\tExcluded: '%s'" % options.filename)
                continue
            buf = open(options.filename).read()
            buf = buf.replace("\r\n", "\n")
            #FIXME buf = buf.decode("ascii", errors="ignore")
            stmt_list = parse.parse(buf if buf[-1] == '\n' else buf + '\n')
            for i in stmt_list:
                print(i)
                print(type(i))

            if not stmt_list:
                continue
            if not options.no_resolve:
                G = resolve.resolve(stmt_list)
            if not options.no_backend:
                s = backend.backend(stmt_list).strip()
            if not options.output:
                f = splitext(basename(options.filename))[0] + ".py"
                with open(f, "w") as fp:
                    print_header(fp)
                    fp.write(s)
            else:
                fp.write(s)
        except KeyboardInterrupt:
            break
        except:
            nerrors += 1
            traceback.print_exc(file=sys.stdout)
            if options.strict:
                break
        finally:
            pass
    if nerrors:
        print("Errors:", nerrors)

main()
