'''
Created on Feb 5, 2016

@author: Roman
'''
from oauth2client import tools
from progressbar import ProgressBar, Percentage, Bar
import os
import uuid
import shutil
import decimal
import lxml.etree as ET
#import xml.etree.ElementTree as ET
import local_file as lf
import remote_file as rf

class PlaylistParser(object):
    '''
    classdocs
    '''
    
    _inputFiles = []
        
                 
    def clean(self, tree):
        for case in tree.iter('file'):
            for playOutcome in case.findall('playoutcome'):  
                playOutcome.getparent().remove(playOutcome)   
                              
            for playLog in case.findall('playlog'):
                playLog.getparent().remove(playLog) 
                
            for replayFile in case.findall('replayfile'):
                replayFile.getparent().remove(replayFile)
        
        for test in tree.iter('test'):
            for playOutcome in test.findall('playoutcome'):  
                playOutcome.getparent().remove(playOutcome)
                
    
    def parse_reference(self, referenceFile):
        if not referenceFile.exists():
            print('Reference file does not exist, creating one: ' + referenceFile.get_name())
            shutil.copy(self._inputFiles[0].get_name(), referenceFile.get_name())
            
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(referenceFile.get_name(), parser)
        self.clean(tree)
        return tree
        

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
            idNode = self.add_node(refCase, 'id')
            idNode.text = str(uuid.uuid4())
            
            self.increment_node(refCase, 'runs')
            
            testResult = newCase.find('playoutcome').text.lower().replace(" ", "")
            self.increment_node(refCase, testResult)
                            
    
    def calculate_rates(self, referenceTree):
        for case in referenceTree.iter('file'):
            runs = case.find('runs')
            sucsess_runs = case.find('playsucceeded')
            if sucsess_runs is not None:
                number_of_runs = decimal.Decimal(runs.text)
                number_of_sucsess_runs = decimal.Decimal(sucsess_runs.text)
                sucsessRate = number_of_sucsess_runs / number_of_runs
                rate = self.add_node(case, 'rate')
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
        
        self.calculate_rates(referenceTree)
                                                                                                    
        
    def parse(self):
        print ('\nCrawling...')
        decimal.getcontext().prec = self._precision
        referenceTree = self.parse_reference(self._outputFile)
        count = 0
        for inputFile in self._inputFiles:
            print('Processing: ' + inputFile.get_name())
            parser = ET.XMLParser(remove_blank_text=True)
            playlistTree = ET.parse(inputFile.get_name(), parser)
            self.update_reference(referenceTree, playlistTree)
            #Save from time to time
            count += 1
            if count > 10:
                referenceTree.write(self._outputFile.get_name())
                count = 0

        referenceTree.write(self._outputFile.get_name(), pretty_print=True)
        print('\n All reports processed, report file: ' + self._outputFile.get_name())

    def __init__(self):
        
        try:
            import argparse
            argumentParser = argparse.ArgumentParser(parents=[tools.argparser])
            argumentParser.add_argument('--input', '-i', help='URL address of TestApplication playlist', type=str, required=True)
            argumentParser.add_argument('--output', '-o', help='URL address for Statistics Log', type=str, required=True)
            argumentParser.add_argument('--reset', '-r',  help='reset authentification settings', action='store_true')
            argumentParser.add_argument('--precision', '-p',  help='accuracy of sucsess probability', type=int)
            flags = argumentParser.parse_args()
        except ImportError:
            flags = None

        self._precision = 3
        if flags.precision is not None:
            self._precision = flags.precision
 
        if os.path.isdir(flags.input):
            self._inputFiles = lf.get_files_in_dir_recursive(flags.input)
        elif os.path.isfile(flags.input):
            self._inputFiles.append(lf.LocalFile(flags.input))
        elif rf.is_url(flags.input):
            self._inputFiles.append(rf.RemoteFile(flags.input, flags))
        else:
            raise ValueError('input file type is not supported')

        if rf.is_url(flags.output):
            self._outputFile = rf.RemoteFile(flags.output, flags)
        else:
            self._outputFile = lf.LocalFile(flags.output)