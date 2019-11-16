from time import localtime
import time
import dirsync
import os
import logging
import platform
import sys
import shutil
import tarfile
import datetime
from dateutil import relativedelta
import  threading
#defining global vars
current_local_time=localtime()
script_dir=os.path.dirname(os.path.realpath(__file__))
script_file=os.path.realpath(__file__)

def make_archive(dest_target):
	#print(dest_target)
	str_date=(datetime.datetime.now()).strftime('%d-%m-%Y')
	tar_file=os.path.join(os.path.dirname(dest_target),str(int(time.time())))+'_'+str_date+'.tar.gz'
	EXCLUDE_FILES = [tar_file]	
	tar = tarfile.open(tar_file, "w:gz")
	tar.add(dest_target, filter=lambda x: None if x.name in EXCLUDE_FILES else x)
	tar.close()

#os.path.realpath(__file__) to get path to the current file
if(sys.platform=='win32'):
	startup_path=os.path.join(os.path.expanduser('~'),'AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')
	startup_file=os.path.join(startup_path,'pysync.bat')
	if(not os.path.isfile(startup_file)) :
		
		if(os.path.isdir(startup_path)):
			#create startup bath file
			startup_file=open(startup_file,'w+')
			content="python "+os.path.realpath(__file__)+" >> pysync.log"
			startup_file.write(content)
			startup_file.close();
else:
	#Put this in /etc/init (Use /etc/systemd in Ubuntu 15.x), /etc/init.d
	'''
		#pysync.conf
		start on runlevel [2345]
		stop on runlevel [!2345]

		exec /path/to/script.py
	'''
def eo_backup():	
	#if today is saturday then take backup....
	# here if time.tm_wday 0 means Monday
	#if(current_local_time.tm_wday==5):	
	if(True):		
		#gather all source paths
		src=open(os.path.join(script_dir,'source.ini'))
		src_paths=(src.read().split('\n'))

		# #gather all destination paths
		dest=open(os.path.join(script_dir,'destination.ini'))
		dest_paths=(dest.read().split('\n'))

		'''loop through each of the source and 
		put them in the destination folder'''


		for dest_target in dest_paths:
			dest_target=dest_target.strip()

			if(not os.path.isdir(dest_target)):
				continue

			for src_target in src_paths:
				src_target=src_target.strip()

				if(not os.path.isdir(src_target)):
					continue
				#sync(sourcedir, targetdir, action, logger=my_logger, **options)
				'''Chosing one option among the following ones is mandatory
				--diff, -d	Only report difference between sourcedir and targetdir
				--sync, -s	Synchronize content between sourcedir and targetdir
				--update, -u	Update existing content between sourcedir and targetdir'''
				dirsync.sync(src_target,os.path.join(dest_target,os.path.basename(src_target)),'sync',create=True)
				#extract files
				#shutil.unpack_archive(filename,out_dir)
				''' Packing files now '''
			make_archive(dest_target)

			#Archive is done now remove those files.
			for src_target in src_paths:
				src_target=src_target.strip()

				if(not os.path.isdir(src_target)):
					continue
				else:
					shutil.rmtree(os.path.join(dest_target,os.path.basename(src_target)))

			#os.remove(path) //remove file
			#Paren: os.path.dirname(path)
			#shutil.rmtree(path) //Remove entire directory structure including directory

			## List all .tar.gz files which are compressed by us at root of the folder. ##
			file_list=[]
			for root,dirs,files in os.walk(dest_target):
				for file in files:
					if(file.endswith('.tar.gz')):
						file=file.split('_')
						file_list.append(file[0])
				break

			file_list.sort()

			for archive_name in file_list:
				relative_time=datetime.date.today()+relativedelta.relativedelta(days=-1)
				relative_timestamp = time.mktime(relative_time.timetuple())				
				if( int(relative_timestamp) > int(archive_name) ):
					os.remove(archive_name+'.tar.gz')	
#create and starting daemon thread to take backup
eo_backup() #Testing purpose only
# eo_backup_thread=threading.Thread(target=eo_backup, name='eo_backup_thread')
# eo_backup_thread.setDaemon(True)
# eo_backup_thread.start()
