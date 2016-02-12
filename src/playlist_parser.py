'''
Created on Feb 5, 2016

@author: Roman
'''
from oauth2client import tools
#import remote_file as rf
import local_file as lf
import os
import shutil
import xml.etree.ElementTree as ET
from progressbar import ProgressBar, Percentage, Bar
import decimal

class PlaylistParser(object):
    '''
    classdocs
    '''
    
    _inputFiles = []
        
                 
    def parse_reference(self, referenceFile):
        if not referenceFile.exists():
            print('Reference file does not exist, creating one: ' + referenceFile.get_name())
            shutil.copy(self._inputFiles[0].get_name(), referenceFile.get_name())
        
        return ET.parse(referenceFile.get_name())
        

    def find_node(self, root, triggerName, caseName):
        for trigger in root.iter('test'):
            if triggerName in trigger.find('name').text:
                for case in trigger.iter('file'):
                    if caseName in case.find('localpath').text:
                        return case
        return None
    
    
    def add_node(self, refCase, nodeName):
        node = refCase.find(nodeName)
        if node is None:
            node = ET.SubElement(refCase, nodeName)
            node.text = '0'
        return node
    
    
    def increment_node(self, refCase, nodeName):
        node = self.add_node(refCase, nodeName)
        node.text = str(int(node.text) + 1) 
        return (int(node.text)) 
    
    
    def update_case(self, refCase, newCase):
        if refCase is not None:
            number_of_runs = self.increment_node(refCase, 'runs')
            
            testResult = newCase.find('playoutcome').text.lower().replace(" ", "")
            number_of_result = self.increment_node(refCase, testResult)
            
            rate = self.add_node(refCase, 'rate')
            if 'playsucceeded' in testResult:
                sucsessRate = decimal.Decimal(number_of_result) / decimal.Decimal(number_of_runs)
                rate.text = str(sucsessRate) 
                
    
    def update_reference(self, referenceTree, playlistTree):
        i = 0
        length = 0
        for entry in playlistTree.iter('file'):
            length += 1
            
        widgets = [Percentage(), Bar()]
        pbar = ProgressBar(widgets=widgets, maxval=length).start()
        for trigger in playlistTree.iter('test'):
            triggerName = trigger.find('name').text
            for case in trigger.iter('file'):
                i += 1
                caseName = case.find('localpath').text
                refCase = self.find_node(referenceTree, triggerName, caseName)
                self.update_case(refCase, case)
                pbar.update(i)
        pbar.finish()
                                                                                    
        
    def parse(self):
        print ('\nCrawling...')
        decimal.getcontext().prec = self._precision
        referenceTree = self.parse_reference(self._outputFile)
        count = 0
        for inputFile in self._inputFiles:
            print('Processing: ' + inputFile.get_name())
            playlistTree = ET.parse(inputFile.get_name())
            self.update_reference(referenceTree, playlistTree)
            #Save from time to time
            count += 1
            if count > 10:
                referenceTree.write(self._outputFile.get_name())
                count = 0

        referenceTree.write(self._outputFile.get_name())
        print('\n All reports processed, report file: ' + self._outputFile.get_name())

    def __init__(self):
        
        try:
            import argparse
            argumentParser = argparse.ArgumentParser(parents=[tools.argparser])
            argumentParser.add_argument('--input_url', '-iu', help='URL address of TestApplication playlist', type=str, required=True)
            argumentParser.add_argument('--output_url', '-ou', help='URL address for Statistics Log', type=str, required=True)
            argumentParser.add_argument('--reset', '-r',  help='reset authentification settings', action='store_true')
            argumentParser.add_argument('--precision', '-p',  help='accuracy of sucsess probability', type=int)
            flags = argumentParser.parse_args()
        except ImportError:
            flags = None

        self._precision = 3
        if flags.precision is not None:
            self._precision = flags.precision
 
        if os.path.isdir(flags.input_url):
            self._inputFiles = lf.get_files_in_dir_recursive(flags.input_url)
        elif os.path.isfile(flags.input_url):
            self._inputFiles.append(lf.LocalFile(flags.input_url))
        #elif rf.is_url(flags.input_url):
            #self._inputFiles.append(rf.RemoteFile(flags.input_url, flags))
        else:
            raise ValueError('input file type is not supported')

        #if rf.is_url(flags.output_url):
            #self._outputFile = rf.RemoteFile(flags.output_url, flags)
        #else:
        self._outputFile = lf.LocalFile(flags.output_url)