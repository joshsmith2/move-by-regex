#!/usr/bin/python

import unittest
import os
import inspect
import shutil
import subprocess as sp
import time
from filecmp import dircmp

import move_by_regex

def smooth_join(*args):
    """
    Join two paths together properly
    """
    out_path = ""
    for arg in args:
        out_path = os.path.join(out_path, arg)
    return os.path.abspath(out_path)

def dirs_match(dir_a,dir_b):
    """Checks whether directories a and b differ in structure or content

    >>> dirs_match('/tmp','/tmp')
    True

    >>> dirs_match('/tmp', '/opt')
    False

    """
    comparison = dircmp(dir_a, dir_b)
    if comparison.left_only or comparison.right_only:
        return False
    else:
        return True

def get_dir_currently_running_in():
    """Returns a full path to the directory this script is being run from.
    """
    current_running_path = os.path.abspath(inspect.stack()[0][1])
    current_running_dir = os.path.dirname(current_running_path)
    return current_running_dir

class TestSimpleTransfer(unittest.TestCase):


    def setUp(self):
        #Set up variables
        self.root = get_dir_currently_running_in()
        self.models = smooth_join(self.root, 'models')
        self.source = smooth_join(self.root, 'source')
        self.dest = smooth_join(self.root, 'dest')
        self.logs = smooth_join(self.root, 'logs')
        self.input = smooth_join(self.models, 'input')
        self.input_file = smooth_join(self.root, 'files_to_move.txt')
        self.test_input = "move_me\nmove_me_too\n# A user comment"

        # Copy model folder
        try:
            shutil.rmtree(self.source)
        except OSError as e:
            error_number = e[0]
            if error_number == 2: #File doesn't exist
                pass
            else:
                print str(e)
                raise
        shutil.copytree(self.input, self.source)
        with open(self.input_file, 'w') as input_file:
            input_file.write(self.test_input)

    def tearDown(self):
        # Remove source entirely and recreate it
        shutil.rmtree(self.source)
        os.remove(self.input_file)


    def test_paths_can_be_loaded_from_input_without_comments(self):
        observed = move_by_regex.get_lines(self.input_file)
        desired = self.test_input.split('\n')[:2]
        assert observed == desired


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    unittest.main(exit=False)