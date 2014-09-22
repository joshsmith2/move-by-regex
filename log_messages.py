"""This module is designed to be imported by any modules which need it, and
contains a class definition which will enable importing and easy modification
of log messages globally."""

class LogMessage:
    def __init__(self):
        logfile_header = "This log file was generated by move_by_regex, a " \
                         "script written by Josh Smith in Q4 2014 to move " \
                         "specified subfolders from one place to another."

        self.logfile_header = logfile_header
