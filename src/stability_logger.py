'''
Created on Feb 5, 2016

@author: Roman
'''

import sys
import getopt
import argparse
from oauth2client import tools
from lib2to3.fixer_util import String

import playlist_parser as parser

def main(argv):
    pp = parser.PlaylistParser()
    pp.parse()

if __name__ == "__main__":
    main(sys.argv[1:])
