#!/usr/bin/python

import argparse
import os

def init_args():
    """ Initialise command line arguments"""
    p = argparse.ArgumentParser(
        description="Move directories whose names, at a given depth, "\
                    "match a given list of files")
    p.add_argument('-p', '--pattern-file', metavar='PATH', dest='pattern_file',
                   help="Path to a file containing patterns to be moved")
    p.add_argument('-s', '--source', metavar='PATH', dest='source',
                   help="Directory containing the data to be moved")
    p.add_argument('-d', '--dest', metavar='PATH', dest='dest',
                   help="The destination")
    return p.parse_args()

def get_lines(from_path):
    """Parse a file and return a list of strings"""
    the_file = os.path.abspath(from_path)
    with open(the_file, 'r') as f:
        return [line.strip() for line in f]

def split_path(path):
    """Given a path, this will split it into a list where each component is
    a level in the filesystem.

    >>> split_path('/tmp/*/buttress//pants/./pig.txt')
    ['tmp', '*', 'buttress', 'pants', 'pig.txt']

    """
    path_list = os.path.normpath(path).split(os.path.sep)
    # The below needed to remove empty entry in case of a leading slash
    if not path_list[0]:
        if path_list:
            return path_list[1:]
    else:
        return path_list

def main():
    args = init_args()
    pattern_file = args.pattern_file
    if pattern_file:
        patterns = get_lines(pattern_file)


if __name__== '__main__':
    import doctest
    doctest.testmod()
    main()