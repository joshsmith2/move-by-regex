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

def path_depth_difference(path1, path2):
    """
    Return the difference in depth of two directories as an integer,
    using os.normpath to resolve references like /./, /../ etc properly.

    >>> path_depth_difference('/william/s/burroughs', '/stephen/king')
    1
    >>> path_depth_difference('/pi/', '/pi/./pins/..')
    0
    """
    path1_depth = len(os.path.normpath(path1).split(os.path.sep))
    path2_depth = len(os.path.normpath(path2).split(os.path.sep))
    return abs(path1_depth - path2_depth)

def search_source_for_patterns(source, patterns):
    """
    Walk the source directory and return a list of paths which match patterns.
    This is the meat. If anything's gone awry, it's probably this function.

    source : str : path
        The source directory to search for patterns
    patterns : list : lists
        A list of patterns
    """
    dirs_to_move = []
    files_to_move=[]

    # Maintaining two lists is easier than comparing unsatisfied with patterns
    unsatisfied = patterns[:]
    satisfied = []

    for root, dirs, files in os.walk(source):
        walk_depth = path_depth_difference(root, source)

        # Since we remove matches as we go, only unsatisfied representing paths
        # which are deeper than we've walked so far are eligible to match.
        possible_patterns = [p for p in unsatisfied if len(p) - 1 >= walk_depth]
        if not possible_patterns:
            continue
        for pattern in possible_patterns:
            for d in dirs:
                if pattern[walk_depth] == d or pattern[walk_depth] == '*':
                    # We've got a match! If that's the end of the pattern,
                    # move this object
                    if len(pattern) - 1 == walk_depth:
                        dir_path = swisspy.smooth_join(root, d)
                        dirs_to_move.append(dir_path)
                        # Remove this dir from dirs to be walked
                        dirs.remove(d)
                        unsatisfied.remove(pattern)
                        satisfied.append(pattern)
            for f in files:
                if pattern[walk_depth] == f or pattern[walk_depth] == '*':
                    if len(pattern) == walk_depth - 1:
                        file_path = swisspy.smooth_join(root, f)
                        files_to_move.append(file_path)
                        files.remove(f)
                        unsatisfied.remove(pattern)
                        satisfied.append(pattern)

    paths_not_matched = [os.path.sep.join(u) for u in unsatisfied]
    paths_matched = [os.path.sep.join(s) for s in satisfied]

    out_dict = {'dirs_to_move':dirs_to_move,
                'files_to_move':files_to_move,
                'paths_matched':paths_matched,
                'paths_not_matched':paths_not_matched}
    return out_dict


def move_by_regex(source, dest, paths_file):
    swisspy_path = swisspy. get_dir_currently_running_in()
    current_dir = swisspy.smooth_join(swisspy_path, '..')
    if not paths_file:
        paths_file = swisspy.smooth_join(current_dir, 'enter_paths_here.txt')
    paths = get_lines(paths_file)
    patterns = get_patterns(paths)
    paths_to_move = search_source_for_patterns(source, patterns)

def main():
    args = init_args()
    pass

if __name__== '__main__':
    import doctest
    doctest.testmod()
    main()