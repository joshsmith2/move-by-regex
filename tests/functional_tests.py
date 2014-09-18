#!/usr/bin/python

"""

Functional tests and roadmap for development of move-by-regex.


"""
import unittest
import os

class TransferTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # MINIMUM VIABLE PRODUCT

    # Accept strings (e.g project numbers) from a text file
    # and move any folders named after them from source to dest.
    def test_move_files_matching_string(self):
        pass

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

    def null_test(self):
        assert True

if __name__ == '__main__':
    unittest.main()
