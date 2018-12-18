#!/usr/bin/python3
import sys

# REPORT FILE
reportfile = open(sys.argv[1], "a")
reportfile.write('TEST:         [' + sys.argv[0] + ']\n')
reportfile.write('RESULT:       [OK]')
reportfile.close()