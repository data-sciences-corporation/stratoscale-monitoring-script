#!/usr/bin/python3
########################################################################################################################
#                                           Stratoscale - Monitoring Script                                            #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# INTRODUCTION:                                                                                                        #
#   This script is part of a toolset which is being developed to help monitor and maintain a customer's                #
#   Stratoscale environment. It will monitor multiple components in the Stratoscale stack, which are otherwise         #
#   not monitored.                                                                                                     #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# MODULE DETAILS:                                                                                                      #
#   This module is for TODO                                                                                            #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# CHANGELOG                                                                                                            #
# v0.1 - 18 December 2018 (Richard Raymond)                                                                            #
#   - Template                                                                                                         #
#                                                                                                                      #
########################################################################################################################
import sys

# PARAMETERS
# 1 - Script name, 2 - Root path of calling script, 3 - Report filename

# VARIABLES
result = 0                                                                  # Init OK/NOK marker
error_info = "NO ERROR DATA PROVIDED"                                       # Init error data variable

# ----------------------------------------------------------------------------------------------------------------------
# TEST SCRIPT DATA GOES HERE

# ----------------------------------------------------------------------------------------------------------------------

# UPDATE REPORT FILE
reportfile = open(sys.argv[2] + '/Reports/' + sys.argv[3] + '.txt', "a")    # Open the current report file
reportfile.write('TEST:         [' + sys.argv[1] + ']\n')                   # Open test section in report file
if result == "1":                                                           # Check if test was succesful
    reportfile.write('RESULT:       [OK]')                                  # Write success out to report file
else:                                                                       # ELSE
    reportfile.write('RESULT:       [NOK]')                                 # Write fail out to report file
    errorfilename = sys.argv[3] + "_" + sys.argv[1]                         # Create a error_reportfile
    errorfile = open(sys.argv[2] + '/Reports/' + errorfilename + '.txt', "w+")  # Create error report file
    errorfile.write(error_info)                                             # Write error data to error file
    errorfile.close()                                                       # Close error file
reportfile.write('\n----------------------------------------------------------------------------\n')
reportfile.close()                                                          # Close report file
