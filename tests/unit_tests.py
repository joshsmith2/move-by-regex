#!/usr/bin/python

import unittest
import os
import inspect
import shutil
import subprocess as sp
import time
from filecmp import dircmp
import swisspy

import move_by_regex

class TestSimpleTransfer(unittest.TestCase):


    def setUp(self):
        #Set up variables
        swisspy_root = swisspy.get_dir_currently_running_in()
        self.root = swisspy.smooth_join(swisspy_root, '..')
        self.models = swisspy.smooth_join(self.root, 'models')
        self.source = swisspy.smooth_join(self.root, 'source')
        self.dest = swisspy.smooth_join(self.root, 'dest')
        self.logs = swisspy.smooth_join(self.root, 'logs')
        self.input = swisspy.smooth_join(self.models, 'input')
        self.input_file = swisspy.smooth_join(self.root, 'files_to_move.txt')
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
        with open(self.input_file, 'w') as input_file:
            input_file.write(self.test_input)

    def tearDown(self):
        shutil.rmtree(self.source)
        os.remove(self.input_file)

    def test_paths_can_be_loaded_from_input_without_comments(self):
        observed = move_by_regex.get_lines(self.input_file)
        desired = self.test_input.split('\n')[:-1]
        assert observed == desired


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    unittest.main(exit=False)