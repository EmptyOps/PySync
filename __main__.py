import datetime
import os
import tarfile
import sys
from dateutil import relativedelta
import shutil
import subprocess
#######################################################################
# make archive from source directory to the destination directory
#######################################################################
def make_archive(src,dest,dest_dir):
    dest=os.path.join(dest,dest_dir)
    src=os.path.realpath(src)
    dest=os.path.realpath(dest)

    #make destination path if not exists...
    if not os.path.exists(dest):
        os.makedirs(dest, exist_ok=True)
    
    dest=os.path.join(dest,os.path.basename(src))            
    tar = tarfile.open(dest+'.tar.gz', "w:gz")
    tar.add(src)
    tar.close()
#######################################################################
# function to check if command exists
#######################################################################
def is_tool(command):
    return shutil.which(command) is not None
#######################################################################
# Dump database
#######################################################################
def db_dump(destination_dir,archive_parent,user,password):
    dump_destination=(os.path.join(destination_dir,archive_parent,'DB'))
    #make dirs if does not exists
    os.makedirs(dump_destination, exist_ok=True)
    if(is_tool('mysqldump')):
        for db in open(os.path.join(os.path.dirname(__file__), "db.ini"), "r"):
            db=db.strip()
            os.popen('mysqldump --user=%s  --password=%s  --result-file="%s" --databases %s' % (user,password,os.path.join(dump_destination,"%s.sql"%db),db))
    else:
        print("Please add mysqldump to PATH environment variable")
#######################################################################
# maintainence code
#######################################################################
def maintainence(dest):

    ## List all .tar.gz files which are compressed by us at root of the folder. ##
    dir_list={}
    for root,dirs,files in os.walk(dest):
        for _dir in dirs:
            dir_time=int(datetime.datetime.strptime(_dir,"%d-%m-%Y [%H-%M-%S]").timestamp())
            dir_list[dir_time]=_dir
        break
    sorted(dir_list) #sorted(file_list,reverse=True)

    for _dir in dir_list:
        #get timestamp of past six month before current time.
        relative_time=int((datetime.datetime.now()+relativedelta.relativedelta(months=-6)).timestamp())
        if( int(relative_time) > int(_dir) ):
            if(os.path.isdir(os.path.join(dest,dir_list.get(_dir)))):
                shutil.rmtree(os.path.join(dest,dir_list.get(_dir)))

#######################################################################
# Function to determine the run
#######################################################################
def can_make_run(current_time):

    #dir destination of config folder
    config_dir=os.path.join(os.path.dirname(__file__),'config')
    #make one if not exists our config dir
    os.makedirs(config_dir, exist_ok=True)
    #the file to hold last ran time stamp
    last_run_config=os.path.join(os.path.dirname(__file__),'config/last_run')

    #if current day is saturday return true else false
    if(datetime.datetime.today().weekday() == 5):
        return True
    else:
        if (not os.path.isfile(last_run_config)):
            last_run_file=open(last_run_config,'w+')
            last_run_file.write(str(int(current_time.timestamp())))
            return True
        else:
            last_run_file=open(last_run_config,'r+')
            last_run_time=last_run_file.readline().strip()
            relative_time = int((current_time + relativedelta.relativedelta(days=-6)).timestamp())
            if (int(relative_time) > int(last_run_time)):
                return True
            else:
                return False

#######################################################################
# main execution - begins
#######################################################################
if (sys.platform == 'win32'):
    startup_path = os.path.join(os.path.expanduser('~'),
                                'AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    startup_file = os.path.join(startup_path, 'pysync.bat')
    if (not os.path.isfile(startup_file)):

        if (os.path.isdir(startup_path)):
            # create startup bath file
            startup_file = open(startup_file, 'w+')
            content = "python " + os.path.abspath(os.path.dirname(__file__))+ " >> "+os.path.join(os.path.abspath(os.path.dirname(__file__)),"pysync.log")
            startup_file.write(content)
            startup_file.close()
else:
    # Put this in /etc/init (Use /etc/systemd in Ubuntu 15.x), /etc/init.d
    '''
        #pysync.conf
        start on runlevel [2345]
        stop on runlevel [!2345]
        exec /path/to/script.py
    '''

#current time
current_time=datetime.datetime.now() #date-month-year [hours-minute-sec]
db_user='root'
db_password=''
if(can_make_run(current_time)):
    #if(True):
    #date formated directory name.
    archive_parent=current_time.strftime("%d-%m-%Y [%H-%M-%S]")
    for destination_dir in open(os.path.join(os.path.dirname(__file__),"destination.ini"),"r"):
        destination_dir=destination_dir.strip()

        for source_dir in open(os.path.join(os.path.dirname(__file__),"source.ini"),"r"):
            source_dir=source_dir.strip()

            if (not os.path.isdir(source_dir)):
                continue
            make_archive(source_dir,destination_dir,archive_parent)
            db_dump(destination_dir,archive_parent,user=db_user,password=db_password)
        maintainence(destination_dir)