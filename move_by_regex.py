#!/usr/bin/python

import argparse
import os
import swisspy
import shutil

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

def glob_equal(candidate, match_to, glob='*'):
    """
    >>> glob_equal('hive', 'hive')
    True
    >>> glob_equal('hive','handrews')
    False
    >>> glob_equal('anything', '*')
    True
    >>> glob_equal('anything', '&', glob='&')
    True
    """
    if candidate == match_to or match_to == glob:
        out = True
    else:
        out = False
    return out

def get_redundant_patterns(from_list):
    """
    >>> get_redundant_patterns([['a','b','c'], ['a','b']])
    {'not_redundant': [['a', 'b']], 'redundant': [['a', 'b', 'c']]}
    >>> get_redundant_patterns([['a','*'], ['a','b'], ['a','c','f']])
    {'not_redundant': [['a', '*']], 'redundant': [['a', 'b'], ['a', 'c', 'f']]}
    """
    redundant = []
    not_redundant = sorted(from_list[:], key=len)
    for p in not_redundant:
        # Only interested in pattern longer than p. This will also stop us for
        # checking p itself.
        candidates = [n for n in not_redundant if len(n) >= len(p) if n != p]
        for c in candidates:
            # Guilty until proven innocent
            p_and_c_distinct = False
            for depth in range(0, len(p)):
                if not glob_equal(c[depth], p[depth]):
                    p_and_c_distinct = True

            if not p_and_c_distinct:
                redundant.append(c)
                not_redundant.remove(c)
    return {'redundant': redundant,
            'not_redundant': not_redundant}

def search_source_for_patterns(source, patterns):
    """
    Walk the source directory and return a list of paths which match patterns.
    This is the meat. If anything's gone awry, it's probably this function.

    source : str : path
        The source directory to search for patterns
    patterns : list : lists
        A list of patterns

    :return dict
        {'dirs_to_move' : list of dirs to move,
         'files_to_move' : list of files to move,
         'paths_matched' : list of paths queried and found in source
         'paths_not_matched' : list of paths queried but not found in source
         'redundant_paths' : list of paths not searched as a parent dir had
                             already been found}

    """
    dirs_to_move = []
    files_to_move=[]
    satisfied = []

    # Remove any redundant patterns before going on (e.g ['usr','bin'] is
    # redundant if ['usr'] is present.
    redundant_patterns_output = get_redundant_patterns(patterns)
    redundant_patterns = redundant_patterns_output['redundant']
    to_check = redundant_patterns_output['not_redundant']

    for root, dirs, files in os.walk(source):
        walk_depth = path_depth_difference(root, source)
        # Since we remove matches as we go, only to_check representing paths
        # which are deeper than we've walked so far are eligible to match.
        possible_patterns = [p for p in to_check if len(p) - 1 >= walk_depth]
        if not possible_patterns:
            continue
        for p in possible_patterns:
            for d in dirs:
                if glob_equal(d, p[walk_depth]):
                    # We've got a match! If that's the end of the pattern,
                    # move this object
                    if len(p) - 1 == walk_depth:
                        dir_path = swisspy.smooth_join(root, d)
                        dirs_to_move.append(dir_path)
                        # Remove this dir from dirs to be walked
                        dirs.remove(d)
                        satisfied.append(p)
                        # Only remove this from the list to check if it doesn't
                        # contain a glob
                        if '*' not in p:
                            to_check.remove(p)
            for f in files:
                if glob_equal(f, p[walk_depth]):
                    if len(p) - 1 == walk_depth:
                        file_path = swisspy.smooth_join(root, f)
                        files_to_move.append(file_path)
                        files.remove(f)
                        satisfied.append(p)
                        if '*' not in p:
                            to_check.remove(p)
    sep = os.path.sep
    paths_not_matched = [sep.join(t) for t in to_check if t not in satisfied]
    paths_matched = [sep.join(s) for s in satisfied]
    redundant_paths = [sep.join(r) for r in redundant_patterns]
    out_dict = {'dirs_to_move':dirs_to_move,
                'files_to_move':files_to_move,
                'paths_matched':paths_matched,
                'paths_not_matched':paths_not_matched,
                'redundant_paths':redundant_paths}
    return out_dict

def strip_leading_char(from_str, character='/'):
    """
    >>> strip_leading_char('/tmp')
    'tmp'
    >>> strip_leading_char('tmp')
    'tmp'
    """
    if from_str[0] == character:
        out = from_str[1:]
    else:
        out = from_str
    return out

def move_creating_intermediaries(source, to_move, dest):
    """Move a directory to_move from within source to dest, creating any
    intermediate directories between those two as necessary

    source : str : path
    to_move : str : path
        The directory or file to be moved. Must be within source.
    dest : str : path
    """
    if not os.path.normpath(to_move[:len(source)]) == os.path.normpath(source):
        import sys
        print "{} is not within {}".format(to_move, source)
        sys.exit(-1)
    path_after_source = split_path(strip_leading_char(to_move[len(source):]))
    path_to_create = ""
    for p in path_after_source[:-1]:
        path_to_create = os.path.join(path_to_create, p)
        try:
            dest_path = os.path.join(dest, path_to_create)
            os.mkdir(dest_path)
        except OSError as e:
            if e[0] == 17: # File exists
                pass
            else:
                raise
    final_destination = os.path.join(dest, path_to_create)
    shutil.move(to_move, final_destination)

def move_by_regex(source, dest, paths_file):
    if not paths_file:
        swisspy_path = swisspy. get_dir_currently_running_in()
        current_dir = swisspy.smooth_join(swisspy_path, '..')
        paths_file = swisspy.smooth_join(current_dir, 'enter_paths_here.txt')
    paths = get_lines(paths_file)
    patterns = get_patterns(paths)
    search_result = search_source_for_patterns(source, patterns)
    for dir_path in search_result['dirs_to_move']:
        move_creating_intermediaries(source, dir_path, dest)
    for file_path in search_result['files_to_move']:
        move_creating_intermediaries(source, file_path, dest)


def main():
    args = init_args()
    pass

if __name__== '__main__':
    import doctest
    doctest.testmod()
    main()