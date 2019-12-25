from __future__ import print_function

import os
import os.path
import pickle

from apiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials


class PySyncGoogle:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        # self.sync()
        # self.authenticate()
        # self.auth_client();
        # print(self.make_folder(folder_name='m30'))
        # for lst in self.search_dir('m30')['files']:
        #     self.rem_folder(lst['id'])

    def sync(self, sync_folder='', dir_time=''):
        ''' :param sync_folder: path to last backup folder
            :param dir_time: actual folder name maked as timestamp
            :return: sysc result '''
        self.authenticate()

        if (self.service is not None):
            pysync_dir = self.search_dir('PySync')['files']
            pysync__dir_id = None
            # Create PySync folder if not exists.
            if pysync_dir and len(pysync_dir):
                pysync__dir_id = pysync_dir[0]['id']
            else:
                pysync__dir_id = self.make_folder('PySync')['id']

            backup_dir = self.search_dir(dir_time, pysync__dir_id)['files']
            backup_dir_id = None
            if backup_dir and len(backup_dir):
                backup_dir_id = backup_dir[0]['id']
            else:
                backup_dir_id = self.make_folder(dir_time, pysync__dir_id)['id']

            target_dir = os.path.join(sync_folder, dir_time)
            if (os.path.isdir(target_dir)):
                for item in os.scandir(target_dir):
                    self.upload(os.path.join(target_dir, item.name), backup_dir_id, item)

    def upload(self, path, parent_id, meta):
        '''if(os.path.isdir(path)):
            dir_id = self.mkdir_if_not(os.path.basename(path),parent_id)
            for item in os.scandir(path):
                self.upload(os.path.join(path,item.name),dir_id,item)
        else:'''
        if os.path.isfile(path):
            file_metadata = {
                'name': meta.name,
                # 'mimeType': 'application/vnd.google-apps.spreadsheet'
                'mimeType': 'application/octet-stream'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
            media = MediaFileUpload(path,
                                    mimetype='application/octet-stream',
                                    resumable=True)
            file = self.service.files().create(body=file_metadata,
                                               media_body=media,
                                               fields='id').execute()

    def mkdir_if_not(self, dir, parent_id):
        if (self.service):
            search_res = self.search_dir(dir, parent_id)['files']
            dir_id = None
            if search_res and len(search_res):
                dir_id = search_res[0]['id']
            else:
                dir_id = self.make_folder(dir, parent_id)['id']
            return dir_id
        else:
            return False

    def rem_folder(self, dir_id):
        response = self.service.files().delete(fileId=dir_id).execute()
        response = self.service.files().emptyTrash().execute()

    def make_folder(self, folder_name='', parent_id=None):
        body = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        if parent_id:
            body['parents'] = [parent_id]
        return self.service.files().create(body=body).execute()

    def search_dir(self, folder_name='', parent=''):

        query = "mimeType='application/vnd.google-apps.folder' and name='" + folder_name + "'"
        if (parent is not ''):
            query += " and parents='" + parent + "'"

        return self.service.files().list(q=query,
                                         spaces='drive',
                                         fields='nextPageToken, files(id, name)',
                                         pageToken=None).execute()

    def authenticate(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secrets.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)

    def auth_client(self):

        credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', self.SCOPES)
        self.service = build('drive', 'v3', http=credentials.authorize(Http()))

        request = self.service.files().list().execute()
        files = request.get('items', [])
        for f in files:
            print(f)


google = PySyncGoogle()
