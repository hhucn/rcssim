#!/usr/bin/env python3

import argparse
import functools
import itertools
import multiprocessing
import subprocess
import os
import shlex
import re


def gather_files(dir, output_dir):
    """ Returns (input_fn, output_fn) tuples """
    for base, _, files in os.walk(dir):
        for f in files:
            basename, ext = os.path.splitext(f)
            if ext != '.svg':
                continue
            in_fn = os.path.join(base, f)
            out_fn = os.path.join(output_dir, basename + '.pdf')
            yield (in_fn, out_fn)

def render(fns):
    in_fn, out_fn = fns
    cmd = [
        'inkscape', '--without-gui', in_fn,
        '--export-dpi', '300',
        '--export-pdf', out_fn]

    print(' '.join(
        c if re.match(r'^[0-9a-fA-F_\.]+$', c) else shlex.quote(c)
        for c in cmd))
    subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dirs', metavar='DIR', nargs='+')
    parser.add_argument('--output-dir', metavar='DIR', default='img_pdf')
    args = parser.parse_args()

    all_files = itertools.chain(
        *[gather_files(d, args.output_dir) for d in args.dirs])

    pool = multiprocessing.Pool()
    pool.imap(render, all_files)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
