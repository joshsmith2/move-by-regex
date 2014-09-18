#!/usr/bin/python

"""

Functional tests and roadmap for development of move-by-regex.


"""
import unittest
import os
import shutil
import inspect
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
        root = self.get_dir_currently_running_in()
        input = smooth_join(root, 'models', 'input')
        source = smooth_join(root, 'source')
        input_file = smooth_join(root, 'files_to_move.txt')

        # Copy model folder
        try:
            shutil.rmtree(source)
        except OSError as e:
            error_number = e[0]
            if error_number == 2: #File doesn't exist
                pass
            else:
                print str(e)
                raise

        shutil.copytree(input, source)

        with open(input_file, 'w') as input_file:
            input_file.write('move_me\nmove_me_too')

    def tearDown(self):
        # Initialise paths
        root = self.get_dir_currently_running_in()
        source = smooth_join(root, 'source')
        input_file = smooth_join(root, 'files_to_move.txt')

        # Remove source entirely and recreate it
        shutil.rmtree(source)
        os.remove(input_file)

    def get_dir_currently_running_in(self):
        """Returns a full path to the directory this script is being run from.
        """
        current_running_path = os.path.abspath(inspect.stack()[0][1])
        current_running_dir = os.path.dirname(current_running_path)
        return current_running_dir

    def universals(self):
        """
        A way of having global variables without polluting the namespace.
        """

    def test_always_pass(self):
        assert True

    # MINIMUM VIABLE PRODUCT

    # Accept strings (e.g project numbers) from a text file
    # and move any folders named after them from source to dest.
    def test_move_files_matching_string(self):
        root = self.get_dir_currently_running_in()
        to_move = smooth_join(root, 'files_to_move.txt')
        dest = smooth_join(root, 'dest')
        goal = smooth_join(root,
                           'models',
                           'output_test_move_files_matching_string')

        ### CALL TO FUNCTION GOES HERE ###

        assert dirs_match(dest, goal)


    # Check for matches at / between given depths of the file path

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
