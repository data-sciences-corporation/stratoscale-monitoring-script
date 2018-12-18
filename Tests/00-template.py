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
# v0.2 - 18 December 2018 (Richard Raymond)                                                                            #
#   - YAML Config file handling.                                                                                       #
#   - Added deeper error message customization (define error types in config.yaml)                                     #
#                                                                                                                      #
########################################################################################################################
import sys
import yaml

# PARAMETERS
# 1 - Script name, 2 - Root path of calling script, 3 - Report filename

# VARIABLES
config = yaml.load(open(sys.argv[2] + '/config.yml', 'r'))                  # Pull in config information from YML file.
result = 0                                                                  # Init OK/NOK marker
error_message = "NO ERROR"                                                  # Error message to provide overview of issue
error_data = "NO ERROR DATA PROVIDED"                                       # Full error contents

# ----------------------------------------------------------------------------------------------------------------------
# TEST SCRIPT DATA GOES HERE

# ----------------------------------------------------------------------------------------------------------------------

# UPDATE REPORT FILE
reportfile = open(sys.argv[2] + '/Reports/' + sys.argv[3] + '.txt', "a")    # Open the current report file
reportfile.write('TEST:         [' + sys.argv[1] + ']\n')                   # Open test section in report file
reportfile.write('RESULT:       [' + config['errortypes'][result] + ']')  # Add test status
if result != 0:                                                             # Check if test wasn't successful
    errorfilename = sys.argv[3] + "_" + sys.argv[1]                         # Create a error_reportfile
    errorfile = open(sys.argv[2] + '/Reports/' + errorfilename + '.txt', "w+")  # Create error report file
    errorfile.write(error_data)                                             # Write error data to error file
    errorfile.close()                                                       # Close error file
    reportfile.write(" : " + error_message + '\n')                          # Add error message to report
    reportfile.write(" Please look at [" + errorfilename + ".txt] for further details.")
reportfile.write('\n----------------------------------------------------------------------------\n')
reportfile.close()                                                          # Close report file
