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
import yaml                                                             # For reading the config file

# VARIABLES

# SPLASH SCREEN
print('STRATOSCALE - QUICK MONITOR')

# CREATE SESSION REPORT FILE
rootpath = os.getcwd()                                                  # Get the root path
now = datetime.datetime.now()                                           # Get the date & time (for the filename)
reportfilename = now.strftime("%Y%m%d_%H%M")                            # Create the filename
reportfilename = 'report-' + reportfilename                             # Append the prefix [report-] to the filename
reportfile = open(rootpath + '/Reports/' + reportfilename + '.txt', "w+")  # Create a report file.
reportfile.close()                                                      # Close the report file for later editing.

# RUN THROUGH ALL TESTS
scripts = os.listdir(rootpath + '/Tests')                               # Get the list of scripts in the tests folder
for i in scripts:                                                       # For each script DO
    subprocess.call(['python', 'Tests/' + i, i[:-3], rootpath, reportfilename])  # Run the test script

# READ OUT TEST RESULTS, COMPRESS AND EMAIL RESULTS
reportfile = open(rootpath + '/Reports/' + reportfilename + '.txt', "r")  # Open the report file
print(reportfile.read())                                                # Read rge report file out to the user.
reportfile.close()                                                      # Close the report file for later editing.
