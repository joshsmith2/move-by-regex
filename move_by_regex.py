#!/usr/bin/python

import argparse
import os
import swisspy

def init_args():
    """ Initialise command line arguments"""
    p = argparse.ArgumentParser(
        description="Move directories whose names, at a given depth, "\
                    "match a given list of files")
    p.add_argument('-p', '--paths-file', metavar='PATH', dest='paths_file',
                   help="Path to a file containing patterns to be moved")
    p.add_argument('-s', '--source', metavar='PATH', dest='source',
                   help="Directory containing the data to be moved")
    p.add_argument('-d', '--dest', metavar='PATH', dest='dest',
                   help="The destination")
    return p.parse_args()

def get_lines(from_path, get_comments=False, comment_char='#'):
    """Parse a file and return a list of strings, ignoring comments if
    requested.

    from_path : path
        The path to the file to be parsed.
    get_comments : bool
        If False, ignore lines starting with comment_char
        Default: False
    comment_char : str
        Character denoting comment lines
        Default : '#'
    """
    the_file = os.path.abspath(from_path)
    with open(the_file, 'r') as f:
        if get_comments:
            out_list = [line.strip() for line in f]
        else:
            out_list = [line.strip() for line in f if line[0] != comment_char]
    return out_list

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

def get_patterns(paths):
    """Take a list of paths, return a list of lists containing split patterns
    for those paths

    >>> get_patterns(['/tmp/gog', '/tmp/brine/*/pan'])
    [['tmp', 'gog'], ['tmp', 'brine', '*', 'pan']]
    """
    patterns = []
    for p in paths:
        patterns.append(split_path(p))
    return patterns

def main():
    args = init_args()
    current_dir =swisspy. get_dir_currently_running_in()
    paths_file = args.paths_file
    if not paths_file:
         paths_file = swisspy.smooth_join(current_dir, 'enter_paths_here.txt')
    paths = get_lines(paths_file)



if __name__== '__main__':
    import doctest
    doctest.testmod()
    main()