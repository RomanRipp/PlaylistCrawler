'''
Created on Feb 5, 2016

@author: Roman
'''

import httplib2
import os
import io
import oauth2client

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from apiclient.http import MediaIoBaseDownload

class RemoteFile(object):
    '''
    classdocs
    '''

    SCOPES = 'https://www.googleapis.com/auth/drive'
    CLIENT_SECRET_FILE = '../client_secret.json'
    APPLICATION_NAME = 'Drive API Python Quickstart'
    
    LOCAL_NAME = 'temp.xml'    

    def get_credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'drive-python-quickstart.json')
    
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid or self._flags.reset:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if self._flags:
                credentials = tools.run_flow(flow, store, self._flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials


    def open(self):
        
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)

        file_id = '0Bz4c6C1qqWUVRjVVczhJUVBDaXM'
        request = service.files().get_media(fileId=file_id)
        #fh = io.BytesIO()
        self._fh = file(self.LOCAL_NAME, 'w')
        downloader = MediaIoBaseDownload(self._fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print('Download %d%%.' % int(status.progress() * 100))
        self._fh = open(self.LOCAL_NAME, 'r');
        
        
#         results = service.files().list(
#         pageSize=10,fields="nextPageToken, files(id, name)").execute()
#         items = results.get('files', [])
#         if not items:
#             print('No files found.')
#         else:
#             print('Files:')
#         for item in items:
#             print('{0} ({1})'.format(item['name'], item['id']))
        
        
    def close(self):
        self._fh.close()
        os.remove(self.LOCAL_NAME);

    def read(self):
        return self._fh.read()

    def __init__(self, fileURL, flags):
        self._URL = fileURL
        self._flags = flags
        