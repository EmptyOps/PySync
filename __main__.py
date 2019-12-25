'''
# Project: PySync
# Developed By: Mahesh Patel
# Org: Emtyops Technologies
# Objective:
#           - Backup folders and databases on servers and local systems
#               autamation to save time for system admins.
#           - Sync backup archive to online backup drives.
#           - Easy configurable
'''
import os
# /////////////////////////////////////////////////////////////////////////////#
# Imports
# /////////////////////////////////////////////////////////////////////////////#
import platform
import subprocess
import sys

# ------------------------------------------------------------------------------#
# Operational Variables
# ------------------------------------------------------------------------------#
__PLATFORM__ = platform.system()
__BASE_DIR__ = os.path.dirname(__file__)


# ------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------#
class PySync:
    def __init__(self):
        pass

    def daemonize(self, daemon_file):
        '''
        @Doc
            Create daemon process independent to this execution
            which will keep running in background and backup
            until interrupted implecitely/explecitely.
        :__file__: File path which will be daemonized to independent process.
        :return: PID - Process ID of independent process or False if not a file.
        '''

        if os.path.isfile(daemon_file):
            # process creation flag status
            _FLAG = 0
            # pre-executioning function before creation
            _PFN = None

            if (__PLATFORM__ == 'Windows'):
                '''Check if subprocess has FLAGS if system is WIN'''
                if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP'):
                    _FLAG = subprocess.CREATE_NEW_PROCESS_GROUP
                elif hasattr(subprocess, 'DETACHED_PROCESS'):
                    _FLAG = subprocess.DETACHED_PROCESS
            else:
                '''SET Pre-Executional function to create daemon on UNIX'''
                _PFN = os.setpgrp

            independent_process = subprocess.Popen([sys.executable, daemon_file],
                                                   creationflags=_FLAG,
                                                   preexec_fn=_PFN)
            _PID = independent_process.pid
            if _PID:
                return _PID
            else:
                return False
        else:
            return False


# ------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------ #


if __name__ == '__main__':
    PySync = PySync()
    PySync.daemonize('pysync_daemon.py')
