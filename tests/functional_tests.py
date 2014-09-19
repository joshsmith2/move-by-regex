#!/usr/bin/python

"""

Functional tests and roadmap for development of move-by-regex.


"""
import unittest
import os
import shutil
import inspect
import time
from filecmp import dircmp

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

class TransferTest(unittest.TestCase):

    def setUp(self):
        # Initialise paths
        self.root = self.get_dir_currently_running_in()
        self.models = smooth_join(self.root, 'models')
        self.source = smooth_join(self.root, 'source')
        self.input = smooth_join(self.models, 'input')
        self.dest = smooth_join(self.root, 'dest')
        self.input_model = smooth_join(self.models, 'enter_paths_model.txt')
        self.input_file = smooth_join(self.models, 'enter_paths_here.txt')
        self.test_input = "move_me\n" \
                          "*/move_me\n" \
                          "move_me_too/i_should_also_be_moved\n" \
                          "# A user comment"

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

        # Copy and populate input file
        shutil.copy(self.input_model, self.input_file)
        with open(self.input_file, 'a') as input_file:
            input_file.write(self.test_input)

    def tearDown(self):
        # Remove source entirely and recreate it
        shutil.rmtree(self.source)
        os.remove(self.input_file)

    def get_dir_currently_running_in(self):
        """Returns a full path to the directory this script is being run from.
        """
        current_running_path = os.path.abspath(inspect.stack()[0][1])
        current_running_dir = os.path.dirname(current_running_path)
        return current_running_dir

    # MINIMUM VIABLE PRODUCT

    # Accept paths from a text file and move any matching folders or files
    # from source to dest.
    def test_move_files_matching_string(self):
        to_move = self.input_file
        goal = smooth_join(self.models,
                           'output_test_move_files_matching_string')
        ### CALL TO FUNCTION GOES HERE ###

        assert dirs_match(self.dest, goal)

    # Read-only mode which only logs and does not move

    # Generate a log displaying all directories moved

    # NICE FEATURES

    # Accept regex from a text file into which the strings to search for can
    # be placed, and

    # Generate a list showing all files moved

    # Log how much data was moved

    # Stop before moving to check that the last modified time was before a
    # given date. If not, log when this is, on which file, and hopefully
    # whodunnit.

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    unittest.main(exit=False)
