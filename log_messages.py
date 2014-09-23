"""This module is designed to be imported by any modules which need it, and
contains a class definition which will enable importing and easy modification
of log messages globally."""

class LogMessage:
    def __init__(self):
        header = "This log file was generated by move_by_regex, a " \
                 "script written by Josh Smith in Q4 2014 to move " \
                 "specified subfolders from one place to another.\n"
        success_story = "The following {type} were successfully " \
                        "transferred from {source} to {dest}:"
        moved_files_header = "{type} moved:"
        found_files_header = "{type} found:"
        unmatched_header = "The following patterns were not matched:"

        self.header = header
        self.success_story = success_story
        self.moved_files_header = moved_files_header
        self.found_files_header = found_files_header
        self.unmatched_header = unmatched_header
