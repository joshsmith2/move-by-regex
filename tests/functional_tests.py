#!/usr/bin/python

"""

Functional tests and roadmap for development of move-by-regex.


"""
import unittest
import os
import shutil
import inspect
import swisspy
import move_by_regex
import log_messages
import logging
import subprocess as sp

class TransferTest(unittest.TestCase):

    def setUp(self):
        # Initialise paths

        swisspy_root = swisspy.get_dir_currently_running_in()
        self.root = swisspy.swisspy.smooth_join(swisspy_root, '..')
        self.models = swisspy.smooth_join(self.root, 'models')
        self.source = swisspy.smooth_join(self.root, 'source')
        self.logs = swisspy.smooth_join(self.root, 'logs')
        self.dest = swisspy.smooth_join(self.root, 'dest')
        self.input = swisspy.smooth_join(self.models, 'input')
        self.log_file_path = None
        self.log_text = log_messages.LogMessage()
        self.input_model = swisspy.smooth_join(self.models,
                                               'enter_paths_model.txt')
        self.input_file = swisspy.smooth_join(self.models,
                                              'enter_paths_here.txt')
        self.log_mod_dest = os.path.join(self.root, 'log_messages.py')
        self.test_input = "move_me\n" \
                          "*/move_me\n" \
                          "move_me_too/i_should_also_be_moved\n" \
                          "# A user comment"
        #Clean sweep
        self.clear(dirs=[self.source, self.dest, self.logs],
                   files=[self.input_file])
        # Copy model folder
        try:
            shutil.rmtree(self.source)
        except OSError as e:
            error_number = e[0]
            if error_number == 2: #File doesn't exist
                pass
            else:
                raise
        shutil.copytree(self.input, self.source)
        os.mkdir(self.dest)
        os.mkdir(self.logs)

        # Copy and populate input file
        shutil.copy(self.input_model, self.input_file)
        with open(self.input_file, 'a') as input_file:
            input_file.write(self.test_input)

    def tearDown(self):
        self.clear(dirs=[self.source, self.dest, self.logs],
                   files=[self.input_file])
        logging.shutdown()

    def clear(self, dirs=None, files=None):
        """Remove all dirs in dirs and fiiles in files, if they exist."""
        for d in dirs:
            try:
                shutil.rmtree(d)
            except OSError:
                pass
            except TypeError:
                pass
        for f in files:
            try:
                os.remove(f)
            except OSError:
                pass
            except TypeError:
                pass

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
        goal = swisspy.smooth_join(self.models,
                                   'output_test_move_files_matching_string')

        move_by_regex.move_by_regex(self.source, self.dest, self.input_file)

        self.assertTrue(swisspy.dirs_match(self.dest, goal))

    # Generate a local file log displaying all directories moved
    # TODO: At the moment, this test seems to be running twice from Pycharm?
    def test_log_created(self):
        log_file_path = os.path.join(self.logs, 'test_log_created.txt')

        move_by_regex.move_by_regex(self.source,
                                    self.dest,
                                    self.input_file,
                                    log_file=log_file_path)

        self.assertTrue(os.path.exists(log_file_path),
                        msg=log_file_path + " does not exist.")
        with open(log_file_path, 'r') as log_file:
            contents = log_file.read()

        self.assertIn(self.log_text.header, contents)
        self.assertIn(self.log_text.success_story.format(type='directories',
                                                source=self.source,
                                                dest=self.dest),
                      contents)

    # Read-only mode which only logs and does not move
    def test_read_only_mode_works(self):
        self.log_file_path = os.path.join(self.root, 'test_read_only_mode.txt')

        move_by_regex.move_by_regex(self.source,
                                    self.dest,
                                    self.input_file,
                                    log_file=self.log_file_path,
                                    read_only=True)

        # Check destination empty
        self.assertFalse(os.listdir(self.dest), msg="Dest is not empty")

        # Check log created with read only message
        self.assertTrue(os.path.exists(self.log_file_path),
                        msg=self.log_file_path + " does not exist.")
        with open(self.log_file_path, 'r') as log_file:
            contents = log_file.read()
        self.assertIn("Directories found:", contents)



    # Ability to run from command line
    def test_command_line_flags(self):
        self.log_file_path = os.path.join(self.logs, 'test_cl_flags.txt')
        command_list=[
            os.path.join(self.root, '..', 'move_by_regex.py'),
            "-s", self.source,
            "-d", self.dest,
            "-p", self.input_file,
            "-l", self.log_file_path,]
        goal = swisspy.smooth_join(self.models,
                                   'output_test_move_files_matching_string')

        sp.call(command_list)

        self.assertTrue(swisspy.dirs_match(self.dest, goal))
        # Check log created with read only message
        self.assertTrue(os.path.exists(self.log_file_path),
                        msg=self.log_file_path + " does not exist.")
        with open(self.log_file_path, 'r') as log_file:
            contents = log_file.read()
        self.assertIn(self.log_text.success_story.format(type="directories",
                                                         source=self.source,
                                                         dest=self.dest),
                      contents)

    # NICE FEATURES

    # Option to run without logging

    # Regex support within paths

    # Option for a universal match at any depth

    # Generate a list showing all files moved

    # Log how much data was moved

    # Option to syslog

    # Stop before moving to check that the last modified time was before a
    # given date. If not, log when this is, on which file, and hopefully
    # whodunnit.



if __name__ == '__main__':
    import doctest
    doctest.testmod()
    unittest.main(exit=False, verbosity=2)
