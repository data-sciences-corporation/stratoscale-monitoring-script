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
# v0.2 - 18 December 2018 (Richard Raymond)                                                                            #
#   - Added improve report file handling and additional parameters for script calls (script name, root path and report)#
#   - Reads to the report file to output, rather than printing output direct console                                   #
# v0.3 - 19 December 2018 (Richard Raymond)                                                                            #
#   - Added better directory & error handling (directories are defined in the config.yml                               #
# v0.4 - 19 December 2018 (Richard Raymond)                                                                            #
#   - Report archive/compression added                                                                                 #
#                                                                                                                      #
########################################################################################################################

# MODULES
import sys
import os                                                               # For os modules
import datetime                                                         # For dates and time []
import subprocess                                                       # For running os commands
import yaml                                                             # For reading the config file
import zipfile                                                          # For compressing the report info for email

# CONFIG VARIABLES
rootpath = os.getcwd()                                                  # Get the root path
config = yaml.load(open('config.yml', 'r'))                             # Pull in config information from YML file
testdirectory = rootpath + "/" + config['framework']['directory']['test'] + "/"  # Generate directory string for test
reportdirectory = rootpath + "/" + config['framework']['directory']['report'] + "/"  # Generate dir string for reports

# SPLASH SCREEN
print(sys.path)
print('STRATOSCALE - QUICK MONITOR')

# CREATE SESSION REPORT FILE
now = datetime.datetime.now()                                           # Get the date & time (for the filename)
reportfilename = now.strftime("%Y%m%d_%H%M")                            # Create the filename
reportfilename = 'report-' + reportfilename                             # Append the prefix [report-] to the filename
reportfile = open(reportdirectory + reportfilename + '.txt', "w+")      # Create a report file.
reportfile.write('\nSTATUS REPORT [' + config['region']['region1']['name'] + ']\n')
reportfile.write(config['framework']['formatting']['linebreak'] + '\n')
reportfile.close()                                                      # Close the report file for later editing.

# RUN THROUGH ALL TESTS
tests = os.listdir(testdirectory)                                       # Get the list of scripts in tests folder
for test in tests:                                                      # For each script DO
    subprocess.call(['python', testdirectory + test, test[:-3], rootpath, reportfilename])  # Run the test script

# READ OUT TEST RESULTS, COMPRESS AND EMAIL RESULTS
reportfile = open(reportdirectory + reportfilename + '.txt', "r")       # Open the report file
print(reportfile.read())                                                # Read rge report file out to the user.
reportfile.close()                                                      # Close the report file for later editing.

# ZIP REPORT FILES
archive = zipfile.ZipFile(reportdirectory + reportfilename + ".zip", "w")  # Open a zip file
archive.write(config['framework']['directory']['report'])
for report in os.listdir(reportdirectory):                                 # Iterate through all reports
    if ".zip" not in report:                                               # Ignore zip files
        if reportfilename in report:                                       # Check if current report is current
            archive.write(os.path.join(config['framework']['directory']['report'], report))  # Add report to archive
            os.remove(reportdirectory + report)                            # Remove processed report file
archive.close()                                                            # Close the report archive when done

# EMAIL REPORT TO RECIPIENTS
# TODO - v1.0 - Email zipped report data to addresses in recipients
