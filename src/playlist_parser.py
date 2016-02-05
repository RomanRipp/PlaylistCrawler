'''
Created on Feb 5, 2016

@author: Roman
'''
from oauth2client import tools
import remote_file as files

class PlaylistParser(object):
    '''
    classdocs
    '''
        
    def parse(self):
        self._inputFile.open()
        playlist = self._inputFile.read()
        self._inputFile.close()
        print(playlist)


    def __init__(self):
        
        try:
            import argparse
            argumentParser = argparse.ArgumentParser(parents=[tools.argparser])
            argumentParser.add_argument('--input_url', '-iu', help='URL address of TestApplication playlist', type=str, required=True)
            argumentParser.add_argument('--output_url', '-ou', help='URL address for Statistics Log', type=str, required=True)
            argumentParser.add_argument('--reset', '-r',  help='reset authentification settings', action='store_true')
            flags = argumentParser.parse_args()
        except ImportError:
            flags = None

        self._inputFile = files.RemoteFile(flags.input_url, flags)
        self._outputFile = files.RemoteFile(flags.output_url, flags)        