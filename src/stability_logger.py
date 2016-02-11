'''
Created on Feb 5, 2016

@author: Roman
'''
import sys
import playlist_parser as parser

def main(argv):
    pp = parser.PlaylistParser()
    pp.parse()

if __name__ == "__main__":
    main(sys.argv[1:])
