
# PySync

### An easy tool created with python to sync all backup folders and databases to targeted destination folders and google drive for lazy admins.

## Installation
* Clone the repository.
* Install the dependency by `pip install -r requirements.txt` command in your python environment.

## Usage:
1. edit source.ini and put all the source directorie's path one after one on new line.
2. edit destination.ini and put all the destination directorie's path one after one on new line.
3. edit db.ini and add list of databses to backup one after one on new line.
4. change db_user and db_password variable in pysync_daemon.py at line 17 and 18 to dump DB.
5. acquire client_secret.json a google drive api key file and store it to the root directory of the project.
6. start the script as module by `python PySync` from outer directory of the project.
7. You will be prompted to allow through your google drive, please allow it and it is safe.

## Future:
* Customization option.
* Google Drive maintainence module.
* More precise backup plans.
* System cron dependency for linux based system and schedular for windows system.
* System optimization
