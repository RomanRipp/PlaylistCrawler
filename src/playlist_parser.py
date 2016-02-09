'''
Created on Feb 5, 2016

@author: Roman
'''
from oauth2client import tools
import remote_file as rf
import local_file as lf
import os
import xml.etree.ElementTree as et
import shutil

class PlaylistParser(object):
    '''
    classdocs
    '''
    
    _inputFiles = []
        
    def parse_test_cases(self, test):
        results = dict()
        for case in test.findall('file'):
            caseName = case.find('localpath').text
            testResult = case.find('playoutcome').text
            print('---File: ' + caseName)
            results[caseName] = testResult
        return results
       
       
    def parse_tests(self, project):
        results = dict()
        for test in project.findall('test'):
            testName = test.find('name').text
            print('--Test: ' + testName)
            results[testName] = self.parse_test_cases(test)
        return results

       
    def parse_projects(self, solution):
        results = dict()
        for project in solution.findall('project'):
            projectName = project.find('name').text
            print('-Project: ' + projectName)
            results[projectName] = self.parse_tests(project)
        return results


    def parse_solutions(self, root):
        results = dict()
        for solution in root.findall('solution'):
            solutionName = solution.find('name').text
            print('Solution: ' + solutionName)
            results[solutionName] = self.parse_projects(solution)
        return results

        
    def parse_playlist(self, name):
        print('Parsing: ' + name)
        tree = et.parse(name)
        root = tree.getroot()
        return self.parse_solutions(root)
         
         
    def parse_reference(self, referenceFile):
        if not referenceFile.exists():
            print('Reference file does not exist, creating one: ' + referenceFile.get_name())
            shutil.copy(self._inputFiles[0].get_name(), referenceFile.get_name())
        
        return self.parse_playlist(referenceFile.get_name())
        
        
    def update_solution(self, reference, playlist):
        for project in playlist:
            self.update_project()
    
    def update_reference(self, reference, playlist):
        for solution in playlist:
            self.update_solution(reference[solution], playlist[solution])    
        
    def parse(self):
        reference = self.parse_reference(self._outputFile)
        for inputFile in self._inputFiles:
            playlist = self.parse_playlist(inputFile.get_name())
            
#             inputFile.open()
#             playlist = inputFile.read()
#             inputFile.close()
#             self.parse_playlist(playlist)


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
 
        if os.path.isdir(flags.input_url):
            self._inputFiles = lf.get_files_in_dir(flags.input_url)
        elif os.path.isfile(flags.input_url):
            self._inputFiles.append(lf.LocalFile(flags.input_url))
        elif rf.is_url(flags.input_url):
            self._inputFiles.append(rf.RemoteFile(flags.input_url, flags))
        else:
            raise ValueError('input file type is not supported')

        if rf.is_url(flags.output_url):
            self._outputFile = rf.RemoteFile(flags.output_url, flags)
        else:
            self._outputFile = lf.LocalFile(flags.output_url)