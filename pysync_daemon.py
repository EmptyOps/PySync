import datetime
import os
import shutil
import tarfile
import threading
import time

from dateutil import relativedelta

import sync


class PySyncBackup:

    def __init__(self):
        # System variables
        self.DB_USER = 'root'
        self.DB_PASSWORD = ''
        # datetime.datetime(2019,12,20,7,30,0)
        self.CURRENT_TIME = datetime.datetime.now()  # date-month-year [hours-minute-sec]
        self.DIR_TIME = self.CURRENT_TIME.strftime("%d-%m-%Y [%H-%M-%S]")
        self.SYS_DIR = os.path.dirname(__file__)

        self.SOURCE_INI = os.path.join(os.path.dirname(__file__), "source.ini")
        self.DESTINATION_INI = os.path.join(os.path.dirname(__file__), "destination.ini")
        self.DB_INI = os.path.join(os.path.dirname(__file__), "db.ini")
        sync_thread = threading.Thread(target=self.sync)
        sync_thread.start()

    def sync(self):
        while (True):
            if self.is_backup_event():
                src_dirs = self.get_resource(self.SOURCE_INI, filter_dir=True)
                dest_dirs = self.get_resource(self.DESTINATION_INI)

                for dest_dir in dest_dirs:
                    for src_dir in src_dirs:
                        self.make_archive(src_dir, dest_dir, self.DIR_TIME)
                        self.db_dump(dest_dir, self.DIR_TIME, user=self.DB_USER, password=self.DB_PASSWORD)
                    self.maintainence(dest_dir)

                self.make_archive(os.path.join(dest_dirs[-1], self.DIR_TIME, 'DB'), dest_dirs[-1], self.DIR_TIME)
                sync.google.sync(dest_dirs[-1], self.DIR_TIME)
            # sleep time calculation
            _year = int(self.CURRENT_TIME.strftime("%Y"))
            _month = int(self.CURRENT_TIME.strftime("%m"))
            _date = int(self.CURRENT_TIME.strftime("%d"))
            _hour = None
            _minutes = None

            with open(os.path.join(self.SYS_DIR, 'config/schedule'), 'w+') as scheduler_file:
                scheduler_config = scheduler_file.readline().strip()
                if scheduler_config is not '':
                    _time_part = [int(x.strip()) for x in scheduler_config.split(':')]
                    _hour = int(_time_part[0])
                    _minutes = int(_time_part[1])
                else:
                    scheduler_file.write(self.CURRENT_TIME.strftime("%H") + ":" + self.CURRENT_TIME.strftime("%M"))
                    _hour = int(self.CURRENT_TIME.strftime("%H"))
                    _minutes = int(self.CURRENT_TIME.strftime("%M"))

            next_backup_time = datetime.datetime(_year, _month, _date, _hour, _minutes)
            next_backup_time = int((next_backup_time + relativedelta.relativedelta(days=+1)).timestamp())
            sleep_time = int(next_backup_time - self.CURRENT_TIME.timestamp())
            time.sleep(sleep_time)

    def is_backup_event(self):
        # dir destination of config folder
        config_dir = os.path.join(self.SYS_DIR, 'config')
        # make one if not exists our config dir
        os.makedirs(config_dir, exist_ok=True)
        # the file to hold last ran time stamp
        last_run_config = os.path.join(self.SYS_DIR, 'config/last_run')
        # if current day is saturday return true else false
        if datetime.datetime.today().weekday() == 5:
            return True
        else:
            if not os.path.isfile(last_run_config):
                last_run_file = open(last_run_config, 'w+')
                last_run_file.write(str(int(self.CURRENT_TIME.timestamp())))
                return True
            else:
                last_run_file = open(last_run_config, 'r+')
                last_run_time = last_run_file.readline().strip()
                if last_run_time == '':
                    last_run_time = 0

                relative_time = int((self.CURRENT_TIME + relativedelta.relativedelta(days=-6)).timestamp())
                if int(relative_time) > int(last_run_time):
                    return True
                else:
                    return False

    def make_archive(self, src, dest, dest_dir):
        src = os.path.realpath(src)
        dest = os.path.realpath(os.path.join(dest, dest_dir))

        # make destination path if not exists...
        if not os.path.exists(dest):
            os.makedirs(dest, exist_ok=True)

        dest = os.path.join(dest, os.path.basename(src) + '.tar.gz')

        tar = tarfile.open(dest, "w:gz")
        tar.add(src)
        tar.close()

    def is_tool(self, command):
        return shutil.which(command) is not None

    def db_dump(self, destination_dir, archive_parent, user, password):
        dump_destination = (os.path.join(destination_dir, archive_parent, 'DB'))
        # make dirs if does not exists
        os.makedirs(dump_destination, exist_ok=True)
        if (self.is_tool('mysqldump')):
            for db in open(os.path.join(self.SYS_DIR, "db.ini"), "r"):
                db = db.strip()
                os.popen('mysqldump --user=%s  --password=%s  --result-file="%s" --databases %s' % (
                    user, password, os.path.join(dump_destination, "%s.sql" % db), db))
        else:
            self.log("Please add mysqldump to PATH environment variable")

    def maintainence(self, dest):
        # List all .tar.gz files which are compressed by us at root of the folder. ##
        dir_list = {}
        for root, dirs, files in os.walk(dest):
            for _dir in dirs:
                dir_time = int(datetime.datetime.strptime(_dir, "%d-%m-%Y [%H-%M-%S]").timestamp())
                dir_list[dir_time] = _dir
            break
        sorted(dir_list)  # sorted(file_list,reverse=True)

        for _dir in dir_list:
            # get timestamp of past six month before current time.
            relative_time = int((datetime.datetime.now() + relativedelta.relativedelta(months=-6)).timestamp())
            if (int(relative_time) > int(_dir)):
                dir_path = os.path.join(dest, dir_list.get(_dir))
                if (dir_path):
                    shutil.rmtree(dir_path)
                    self.log("Maintainence Mode: removing folder - " + dir_path)

    def get_resource(self, file_path='', filter_files=False, filter_dir=False):
        if os.path.isfile(file_path):
            with open(file_path, "r") as resource:
                resource = [x.strip() for x in resource.readlines() if x.strip() is not '']
                # Return after filtering file resource lists
                if filter_files:
                    resource = [x for x in resource if os.path.isfile(x)]
                    return resource
                # Return after filtering directory resource list
                if filter_dir:
                    resource = [x for x in resource if os.path.isdir(x)]
                    return resource
                # Return if no filtering option is set, i.e. retrun all list
                return resource

    def log(self, msg):
        log_file = open('log.txt', 'a+')
        log_file.write(datetime.datetime.now().timestamp().__str__() + ': ' + msg + '\n');
        log_file.close();


# init backup....
PySyncBackup()
