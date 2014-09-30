#!/usr/bin/python

import logging
import os
import shutil
import swisspy
import subprocess
import unittest

import log_messages
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
        self.log_text = log_messages.LogMessage()
        self.log_file_path = os.path.join(self.logs, 'test_log_output.txt')
        self.input = swisspy.smooth_join(self.models, 'input')
        self.input_model = swisspy.smooth_join(self.models, 'enter_paths_model.txt')
        self.input_file = swisspy.smooth_join(self.root, 'enter_paths_here.txt')
        self.desired_output = swisspy.smooth_join(self.models, 'desired_output')

        self.clear_dirs()

        # Copy model folder
        shutil.copytree(self.input, self.source)
        os.mkdir(self.desired_output)
        shutil.copy(self.input_model, self.input_file)
        os.mkdir(self.dest)
        os.mkdir(self.logs)

    def tearDown(self):
        self.clear_dirs()
        self.remove_all_logging_handlers()
        logging.shutdown()

    def clear_dirs(self):
        # TODO: Do this properly.
        for d in [self.source, self.dest, self.desired_output, self.logs]:
            try:
                shutil.rmtree(d)
            except OSError:
                pass
        try:
            os.remove(self.input_file)
        except OSError:
            pass

    def get_log_contents(self):
        with open(self.log_file_path) as log_file:
            return log_file.read()

    def remove_all_logging_handlers(self):
        """Removes the handlers on all logger instances, in order to ameliorate
        log confusion between tests."""
        existing_loggers = logging.Logger.manager.loggerDict
        for el in existing_loggers:
            existing_loggers[el].handlers=[]

    def test_paths_can_be_loaded_from_input_without_comments(self):
        test_input = "a_path\n# A comment"
        with open(self.input_file, 'a') as input_file:
            input_file.write(test_input)
        observed = move_by_regex.get_lines(self.input_file)
        desired = ['a_path']
        self.assertEqual(observed, desired)

    def set_up_spacer_test(self):
        os.mkdir(swisspy.smooth_join(self.source,'spacer'))
        os.mkdir(swisspy.smooth_join(self.source,'move_only_from_spacer'))
        os.mkdir(swisspy.smooth_join(self.source,
                                     'spacer',
                                     'move_only_from_spacer'))
        # Make model directory to compare with
        os.mkdir(swisspy.smooth_join(self.desired_output, 'spacer'))
        os.mkdir(swisspy.smooth_join(self.desired_output,
                                     'spacer',
                                     'move_only_from_spacer'))

    def test_check_search_source_for_patterns_returns_correct_dict(self):
        self.set_up_spacer_test()
        test_input = "*/move_only_from_spacer\nnot_found"
        with open(self.input_file, 'a') as input_file:
            input_file.write(test_input)

        operation = move_by_regex.search_source_for_patterns
        observed = operation(self.source,
                            [['*','move_only_from_spacer'],['not_found']])

        desired = {'dirs_to_move':[os.path.join(self.source,
                                                'spacer',
                                                'move_only_from_spacer')],
                    'files_to_move':[],
                    'invalid_regex':[],
                    'paths_matched':['*/move_only_from_spacer'],
                    'paths_not_matched':['not_found'],
                    'redundant_paths':[]}

        self.assertEqual(desired, observed)

    def test_files_within_matched_dirs_not_found_by_search_source(self):
        self.set_up_spacer_test()
        a_file_path = (swisspy.smooth_join(self.source, 'spacer',
                                          'move_only_from_spacer',
                                          'a_file'))
        with open(a_file_path, 'w') as a_file:
            a_file.write("DO NOT FIND ME")

        operation = move_by_regex.search_source_for_patterns
        observed = operation(self.source,
                             [['spacer','move_only_from_spacer'],
                              ['spacer', 'move_only_from_spacer', 'a_file']])


        desired = {'dirs_to_move':[os.path.join(self.source,
                                               'spacer',
                                               'move_only_from_spacer')],
                   'files_to_move':[],
                   'invalid_regex':[],
                   'paths_matched':['spacer/move_only_from_spacer'],
                   'paths_not_matched':[],
                   'redundant_paths':['spacer/move_only_from_spacer/a_file']}

        self.assertEqual(observed,desired)

    def test_move_a_directory_from_the_root(self):
        os.mkdir(os.path.join(self.desired_output, 'move_me'))
        test_input = 'move_me'
        with open(self.input_file, 'a') as input_file:
            input_file.write(test_input)

        move_by_regex.move_by_regex(self.source, self.dest, self.input_file)

        assert swisspy.dirs_match(self.dest, self.desired_output)

    def test_move_a_directory_from_depth_of_1(self):
        self.set_up_spacer_test()
        test_input = "*/move_only_from_spacer"
        with open(self.input_file, 'a') as input_file:
            input_file.write(test_input)

        move_by_regex.move_by_regex(self.source, self.dest, self.input_file)

        self.assertTrue(swisspy.dirs_match(self.dest, self.desired_output))

    def test_glob_matches_more_than_one_file(self):
        test_input = "*/spacer_1"
        with open(self.input_file, 'w') as input_file:
            input_file.write(test_input)

        move_by_regex.move_by_regex(self.source, self.dest, self.input_file)

        should_exist = [swisspy.smooth_join(self.dest, 'depth_2', 'spacer_1'),
                        swisspy.smooth_join(self.dest, 'depth_3', 'spacer_1')]
        for dir in should_exist:
            self.assertTrue(os.path.exists(dir))

    def test_error_generated_on_moving_same_file(self):
        guinea_pig_dir = os.path.join(self.dest, 'move_me')
        os.mkdir(guinea_pig_dir)
        with open(self.input_file, 'w') as input_file:
            input_file.write('move_me')

        move_by_regex.move_by_regex(self.source, self.dest, self.input_file,
                                    self.log_file_path)

        expected_error = "Destination path '%s' already exists" % guinea_pig_dir
        self.assertIn(expected_error, self.get_log_contents())

    def test_log_unmatched_patterns(self):
        with open(self.input_file, 'w') as input_file:
            input_file.write('emperor_zibzob')

        move_by_regex.move_by_regex(self.source, self.dest, self.input_file,
                                    self.log_file_path, log_unmatched=True)

        self.assertIn(self.log_text.unmatched_header, self.get_log_contents())
        self.assertIn('emperor_zibzob', self.get_log_contents())

    def test_correct_behavior_on_no_pattern_file_direct(self):
        expected = self.log_text.no_patterns.format(path_file=self.input_file)

        move_by_regex.move_by_regex(self.source,
                                    self.dest,
                                    log_file=self.log_file_path)

        self.assertIn(expected, self.get_log_contents())

    def test_correct_behavior_on_no_pattern_file_cmd_line(self):
        pattern_file = swisspy.smooth_join(self.root, '..',
                                           'enter_paths_here.txt')
        command_list=[
            os.path.join(self.root, '..', 'move_by_regex.py'),
            "-s", self.source,
            "-d", self.dest,
            "-l", self.log_file_path,]

        expected = self.log_text.no_patterns.format(path_file=pattern_file)

        subprocess.call(command_list)

        self.assertIn(expected, self.get_log_contents())

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    unittest.main(exit=False, verbosity=2)