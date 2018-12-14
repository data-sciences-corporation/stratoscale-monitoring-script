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
#   This module is the primary calling script for the monitoring tool suite.                                           #
#   All tests will be called from this module, for each Stratoscale clout platform.                                    #
#   All of the tests that will be run will be created in "Tests" sub-directory (this script will iterate through       #
#   whatever tests exists there.                                                                                       #
#   Each test script will be responsible for appending it's results to a report file in the "Reports" folder.          #
#   This script will then e-mail that report to all mail recipients references in the "recipients.txt" file.           #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# CHANGELOG                                                                                                            #
# v0.1 - 14 December 2018 (Richard Raymond)                                                                            #
#   - Initial version                                                                                                  #
#                                                                                                                      #
########################################################################################################################

# MODULES
import os
import datetime
import subprocess

# VARIABLES
dashes = '----------------------------------------------------------------------------'

# SPLASH SCREEN
print('STRATOSCALE - QUICK MONITOR')

# 1. Create report file
now = datetime.datetime.now()
filename = now.strftime("%Y%m%d_%H%M")
filename = 'Reports/report-' + filename + '.txt'
reportfile = open(filename, "w+")

# 2. Iterate through test scripts
path = os.getcwd() + '/Tests'                               # Get the working path of the tests folder
scripts = os.listdir(path)                                  # Get the scripts in the tests folder

print(dashes)
for i in scripts:
    scriptname = 'Tests/' + i
    subprocess.call(['python', scriptname, filename])
    print(dashes)

# 3. Send report file to recipients
reportfile.close()
