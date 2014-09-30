#!/usr/bin/python

from django_bits import *
import argparse
import os
import swisspy
import shutil
import logging
import log_messages
import re


class PatternPiece:
    """Part of a pattern, which itself is a divided path.
    E.g:
      path:               '/tmp/'
      pattern:            ['tmp']
      PatternPiece.name:  'tmp'
      PatternPiece.type:  'string'
      ...
    """
    def __init__(self, name,
                 regex_ind_start="regex{",
                 regex_ind_end="}",
                 glob_pattern='*',):
        """Initialises a number of useful variables concerning the object:

        self.name : str
            The string passed as input to create this object - e.g 'tmp' or
            'regex{.*}'
        self.regex_ind_start : str : default 'regex{'
        self.regex_ind_end : str : default '}'
            Used to denote the start and end, respectively, of a string
            to be interpreted as a regex pattern
        self.glob_pattern : str : default '*'
            A wildcard which will match any string

        >>> p = PatternPiece('bramblescrant')
        >>> p.name
        'bramblescrant'
        >>> p.type
        'string'
        >>> p.regex_pattern


        >>> q = PatternPiece('{[Ww]hee+}', regex_ind_start='{', regex_ind_end='}')
        >>> q.name
        '{[Ww]hee+}'
        >>> q.type
        'regex'
        >>> q.regex_pattern
        '[Ww]hee+'

        """
        self.name = name
        self.regex_ind_start = regex_ind_start
        self.regex_ind_end = regex_ind_end
        self.glob_pattern = glob_pattern
        self.regex_pattern = None

        if self.name[:len(self.regex_ind_start)] == self.regex_ind_start and \
           self.name[-len(self.regex_ind_end):] == self.regex_ind_end:
            self.type = 'regex'
            regex_pattern = self.name[len(regex_ind_start):-len(regex_ind_end)]
            self.regex_pattern = regex_pattern
        elif self.name == self.glob_pattern:
            self.type = 'glob'
        else:
            self.type = 'string'

def init_args(current_dir):
    """ Initialise command line arguments"""
    p = argparse.ArgumentParser(
        description="Move directories whose names, at a given depth, "\
                    "match a given list of files")
    p.add_argument('-s', '--source', metavar='path', type=str,
                   dest='source',
                   help="Directory containing the data to be moved")
    p.add_argument('-d', '--dest', metavar='path', type=str,
                   dest='dest',
                   help="The destination")
    p.add_argument('-p', '--paths-file', metavar='path', type=str,
                   dest='paths_file',
                   help="Path to a file containing patterns to be moved")
    p.add_argument('-l', '--log-file', metavar='path', type=str,
                   dest='log_file',
                   help="Path to log file")
    p.add_argument('-r', '--read-only', action='store_true', default=False,
                   dest='read_only',
                   help="Run in read only mode - log but don't move.")
    p.add_argument('--log-unmatched', action='store_true', default=False,
                   dest='log_unmatched',
                   help="Log any paths which were not found in source")
    return p.parse_args()

def init_console_logging():
    """Currently not implemented."""
    # Set up logging to console (WARNING and above)
    to_console = logging.StreamHandler()
    to_console.setLevel(logging.WARNING)
    console_formatter = ('%(name)-16s: %(levelname)-8s %(message)s')
    to_console.setFormatter(console_formatter)
    # Set up a root level handler, and one for this area
    logging.getLogger('').addHandler(to_console)

def init_logging(log_file, log_text):
    """Set up logging objects for a given log file path

    Excellent explanation of how this works here:
    https://docs.python.org/2/howto/logging-cookbook.html

    log_file : str : path
        Path to the human readable log
    log_text : LogMessage object
        Object read from log_messages.py
    """
    log_file = os.path.abspath(log_file)
    # Set up logging to file
    logging.basicConfig(level=logging.INFO,
                        format='%(message)s',
                        datefmt='%m/%d/%Y %H:%M',
                        filename=log_file,
                        filemode='w')
    init_logger = logging.getLogger('mbr.loginit')
    init_logger.info(log_text.header)

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

def join_pattern(pattern):
    """Given a pattern, returns a path

    pattern : list : strings
        A list representing a file path

    >>> join_pattern(['tmp', 'branst'])
    'tmp/branst'
    """
    return os.path.sep.join(pattern)

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

def match(match_to, input):
    """Compare a string using either a glob or regex match, depending on
    whether the defined regex indicators are present. Return true or false.

    match_to : PatternPiece
        PatternPiece objects contain information on what type of string they
        are (see their docs)
    input : str

    # Glob and string matches:
    >>> string_example = PatternPiece('hive')
    >>> match(string_example, 'hive')
    True
    >>> match(string_example,'handrews')
    False
    >>> glob_example = PatternPiece('*')
    >>> match(glob_example, 'anything')
    True

    # Regex matches:
    >>> regex_example = PatternPiece('regex{[Pp]amp}')
    >>> match(regex_example, 'Pamp')
    True
    """
    matches=False
    if match_to.type == 'regex':
        if re.match(match_to.regex_pattern, input):
            matches = True
    else:
        if input == match_to.name or match_to.type == 'glob':
            matches = True
    return matches

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
        candidates = [n for n in not_redundant if len(n) >= len(p) if n != p]
        for c in candidates:
            # Guilty until proven innocent
            p_and_c_distinct = False
            for depth in range(0, len(p)):
                # Conversion to PatternPiece here allows us to use match,
                # which handles globs and regex gracefully
                p_piece = PatternPiece(p[depth])
                if not match(p_piece, c[depth]):
                    p_and_c_distinct = True
            if not p_and_c_distinct:
                redundant.append(c)
                not_redundant.remove(c)
    return {'redundant': redundant,
            'not_redundant': not_redundant}

def search_source_for_patterns(source, patterns,
                               regex_ind_start=None, regex_ind_end=None):
    """
    Walk the source directory and return a list of paths which match patterns.
    This is the meat. If anything's gone awry, it's probably this function.

    source : str : path
        The source directory to search for patterns
    patterns : list : lists
        A list of patterns
    regex_ind_start : str
        String indicating the beginning of a regex pattern
    regex_ind_end : str
        String indicating the end of a regex pattern

    :return dict
        {'dirs_to_move' : list of dirs to move,
         'files_to_move' : list of files to move,
         'paths_matched' : list of paths queried and found in source
         'paths_not_matched' : list of paths queried but not found in source
         'redundant_paths' : list of paths not searched as a parent dir had
                             already been found}
         'invalid_regex' : Invalid regex patterns encountered.

    """
    dirs_to_move = []
    files_to_move=[]
    satisfied = []
    invalid_regex = []

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
        for pattern in possible_patterns:
            pieces = [PatternPiece(p) for p in pattern]
            to_match = pieces[walk_depth]
            for d in dirs[:]:
                try:
                    paths_match = match(to_match, d)
                except Exception:
                    if to_match.regex_pattern not in invalid_regex:
                        invalid_regex.append(to_match.regex_pattern)
                        to_check.remove(pattern)
                        continue
                if paths_match:
                    # We've got a match! If that's the end of the pattern,
                    # move this object
                    if len(pattern) - 1 == walk_depth:
                        dir_path = swisspy.smooth_join(root, d)
                        dirs_to_move.append(dir_path)
                        # Remove this dir from dirs to be walked
                        dirs.remove(d)
                        satisfied.append(pattern)
                        # Only remove this from the list to check if it doesn't
                        # contain a glob
                        non_strings = [q for q in pieces if q.type != 'string']
                        if not non_strings:
                            to_check.remove(pattern)
            for f in files:
                try:
                    paths_match = match(to_match, f)
                except Exception:
                    if to_match.regex_pattern not in invalid_regex:
                        invalid_regex.append(to_match.regex_pattern)
                        to_check.remove(pattern)
                        continue
                if paths_match:
                    if len(pattern) - 1 == walk_depth:
                        file_path = swisspy.smooth_join(root, f)
                        files_to_move.append(file_path)
                        files.remove(f)
                        satisfied.append(pattern)
                        non_strings = [q for q in pieces if q.type != 'string']
                        if not non_strings:
                            to_check.remove(pattern)
    sep = os.path.sep
    paths_not_matched = [sep.join(t) for t in to_check if t not in satisfied]
    paths_matched = [sep.join(s) for s in satisfied]
    redundant_paths = [sep.join(r) for r in redundant_patterns]
    out_dict = {'dirs_to_move':dirs_to_move,
                'files_to_move':files_to_move,
                'invalid_regex':invalid_regex,
                'paths_matched':paths_matched,
                'paths_not_matched':paths_not_matched,
                'redundant_paths':redundant_paths,}
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
    mci_logger = logging.getLogger('mbr.move_ci')
    successfully_moved = []
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
    try:
        shutil.move(to_move, final_destination)
        successfully_moved.append(path_after_source)
    except shutil.Error as e:
        if "Destination path" in e.message and "already exists in e.message":
            mci_logger.info(e)
        else:
            mci_logger.exception("Error encountered while moving " + to_move)
    return successfully_moved

def get_file_stats(source, db_name):
    """Creates a database pertaining to the """

def move_by_regex(source, dest, paths_file="", log_file="", read_only=False,
                  log_unmatched=False):

    # Set up variables
    dir_successes = []
    file_successes = []
    log_text = log_messages.LogMessage()
    # Set up logging
    init_logging(log_file, log_text)
    main_logger = logging.getLogger('mbr.main')
    swisspy_path = swisspy.get_dir_currently_running_in()
    current_dir = swisspy.smooth_join(swisspy_path, '..')
    if not paths_file:
        paths_file = os.path.join(current_dir, 'enter_paths_here.txt')
    if not log_file:
        log_file = os.path.join(current_dir, 'logs', 'move_log.txt')

    paths = get_lines(paths_file)
    main_logger.info("\n".join(paths))
    if paths:
        patterns = get_patterns(paths)
        search_result = search_source_for_patterns(source, patterns)
        if read_only:
            if search_result['dirs_to_move']:
                header = log_text.found_files_header.format(type='Directories')
                main_logger.info(header)
                main_logger.info('\n\t' +\
                                 '\n\t'.join(search_result['dirs_to_move']))
            if search_result['files_to_move']:
                header = log_text.found_files_header.format(type='Files')
                main_logger.info(header)
                main_logger.info('\n\t' +\
                                 '\n\t'.join(search_result['files_to_move']))
        else:
            for dir_path in search_result['dirs_to_move']:
                dir_successes = move_creating_intermediaries(source,
                                                             dir_path,
                                                             dest)
            if dir_successes:
                header = log_text.success_story.format(type='directories',
                                                       source=source,
                                                       dest=dest)
                main_logger.info(header)
                for ds in dir_successes:
                    main_logger.info("\t" + join_pattern(ds))
            for file_path in search_result['files_to_move']:
                file_successes = move_creating_intermediaries(source,
                                                              file_path,
                                                              dest)
            if file_successes:
               header = log_text.success_story.format(type='files',
                                                      source=source,
                                                      dest=dest)
               main_logger.info(header)
               for fs in file_successes:
                   main_logger.info("\t" + join_pattern(fs))
        if log_unmatched:
            main_logger.info(log_text.unmatched_header)
            for p in search_result['paths_not_matched']:
                main_logger.info(p)
    else:
        main_logger.info(log_text.no_patterns.format(path_file=paths_file))

def main():
    swisspy_path = swisspy.get_dir_currently_running_in()
    current_dir = swisspy.smooth_join(swisspy_path, '..')
    args = init_args(current_dir)
    move_by_regex(args.source, args.dest, args.paths_file, args.log_file,
                  args.read_only, args.log_unmatched)

if __name__== '__main__':
    import doctest
    doctest.testmod()
    main()