#!/usr/bin/python

import unittest
import os
import shutil
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
        self.input_model = swisspy.smooth_join(self.models, 'enter_paths_model.txt')
        self.input_file = swisspy.smooth_join(self.models, 'enter_paths_here.txt')
        self.desired_output = swisspy.smooth_join(self.models, 'desired_output')

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
        shutil.copy(self.input_model, self.input_file)
        os.mkdir(self.desired_output)

    def tearDown(self):
        shutil.rmtree(self.source)
        shutil.rmtree(self.desired_output)
        os.remove(self.input_file)

    def test_paths_can_be_loaded_from_input_without_comments(self):
        test_input = "a_path\n# A comment"
        with open(self.input_file, 'a') as input_file:
            input_file.write(test_input)
        observed = move_by_regex.get_lines(self.input_file)
        desired = ['a_path']
        assert observed == desired

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
        assert observed == {'dirs_to_move':[os.path.join(self.source,
                                                        'spacer',
                                                        'move_only_from_spacer')],
                            'files_to_move':[],
                            'paths_matched':['*/move_only_from_spacer'],
                            'paths_not_matched':['not_found'],
                            'redundant_paths':[]}

    def test_files_within_matched_dirs_dont_get_found_by_search_source(self):
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

        assert observed == {'dirs_to_move':[os.path.join(self.source,
                                                         'spacer',
                                                         'move_only_from_spacer')],
                            'files_to_move':[],
                            'paths_matched':['spacer/move_only_from_spacer'],
                            'paths_not_matched':[],
                            'redundant_paths':['spacer/move_only_from_spacer/a_file']}


    def test_move_a_directory_from_specified_depth(self):
        self.set_up_spacer_test()
        test_input = "*/move_only_from_spacer"
        with open(self.input_file, 'a') as input_file:
            input_file.write(test_input)

        move_by_regex.move_by_regex(self.source, self.dest, self.input_file)

        assert swisspy.dirs_match(self.dest, self.desired_output)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    unittest.main(exit=False)