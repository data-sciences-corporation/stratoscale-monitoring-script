#!/usr/bin/python3
import sys

result = 0
error_info = "some sweet-ass error information"







# UPDATE REPORT FILE
reportfile = open(sys.argv[1], "a")
reportfile.write('TEST:         [' + sys.argv[0] + ']\n')
if result == "1":
    reportfile.write('RESULT:       [OK]')
else:
    reportfile.write('RESULT:       [NOK]')
    filename = sys.argv[1] + "_" + sys.argv[0]
    errorfile = open(filename, "w+")
    errorfile.write(error_info)
    errorfile.close()
reportfile.close()
