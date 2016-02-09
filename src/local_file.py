'''
Created on Feb 9, 2016

@author: Roman
'''

import os

def get_files_in_dir(path):
    localFiles = []
    print('Playlists found: ')
    for fileName in os.listdir(path):
        lowerCase = fileName.lower()
        if lowerCase.endswith('.xml') and 'delta' not in lowerCase:
            print (fileName)
            fileName = os.path.join(path, fileName)
            localFiles.append(LocalFile(fileName))
    return localFiles

class LocalFile(object):
    '''
    classdocs
    '''
    
    def get_name(self):
        return self._fileName

    
    def open(self):
        self._file = open(self._fileName, 'r')
        return self._file

    
    def read(self):
        if self._file.closed:
            self._file.open(self._fileName, 'r')
        return self._file.read()

    
    def close(self):
        self._file.close()


    def exists(self):
        return os.path.isfile(self._fileName)

    def __init__(self, fileName):
        '''
        classdocs
        '''
        self._fileName = fileName