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
#   This module is for monitor the base OS mount points, to check if any of the mount points are filling up.           #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# CHANGELOG                                                                                                            #
# v1.0 - 18 December 2018 (Richard Raymond)                                                                            #
#   - Test Template v0.2                                                                                               #
#   - First draft of log space monitoring script. Uses lazy create_bash-run_bash-delete_bash file method.              #
# v1.1 - 19 December 2018 (Richard Raymond)                                                                            #
#   Source: 00-template.py [v0.3] - Requires: monitor.py [v0.4]                                                        #
# v1.2 - 22 March 2019 (Richard Raymond)                                                                               #
#   Source: 00-template.py [v0.4] - Requires: monitor.py [v0.5]                                                        #
#   - Updated script to use latest template (adds improved e-mail granularity), no changes to test code.               #
# v1.3 - 10 April 2019 (Richard Raymond)                                                                               #
#   - Several bug fixes                                                                                                #
# v1.4 - 27 June 2019 (Richard Raymond)                                                                                #
#   - Added actual mount point info to report, so that script caters for all mount points on the base OS, per node.    #
#                                                                                                                      #
########################################################################################################################

# MODULES
import os
import sys
import yaml
import subprocess
import re

# PARAMETERS
# 1 - Script name, 2 - Root path of calling script, 3 - Report filename

# CONFIG VARIABLES
rootpath = sys.argv[2]
config = yaml.load(open(rootpath + '/config.yml', 'r'))                     # Pull in config information from YML file.
testdirectory = rootpath + "/" + config['framework']['directory']['test'] + "/"        # Generate dir for test
reportdirectory = rootpath + "/" + config['framework']['directory']['report'] + "/"    # Generate dir for reports
workingdirectory = rootpath + "/" + config['framework']['directory']['working'] + "/"  # Generate dir for working dir
scriptdirectory = rootpath + "/" + config['framework']['directory']['script'] + "/"    # Generate dir for sub scripts

# SCRIPT VARIABLES
result = 0                                                                  # Initialize OK/NOK marker
error_message = "Log space utilisation is above expected threshold."        # Error message to provide overview
test_data = "Node log space utilisation.\n"                                 # Full error contents

scriptfile = scriptdirectory + sys.argv[1] + ".sh"                          # Create a script file
# ----------------------------------------------------------------------------------------------------------------------
# TEST SCRIPT DATA GOES HERE

# Make a bash script
bashscript = open(scriptfile, "w+")
bashscript.write("#!/bin/bash\nconsul exec 'df -h' | grep '% /' | grep -v ' %'")
bashscript.close()

# Allow execute access
os.chmod(scriptfile, 0o755)                                                 # Force octal data type
process = subprocess.Popen(scriptfile, stdout=subprocess.PIPE)
nodelist, error = process.communicate()
test_data = test_data + nodelist

nodelist = nodelist.rstrip().split("\n")

worstcase = 0
# Test node log space capacities for each node.
#import ipdb; ipdb.set_trace()
for node in nodelist:
    nodename = re.search('(?=[^ ]).*?(?=:)', node).group(0)
    space = re.search('\d*(?=%)', node).group(0)
    if int(space) > 90:
            worstcase = 3
            error_message = error_message + "\n CRITICAL: " + nodename + " - " + space + "% full"
            error_message = error_message + "\n\t" + node
    elif int(space) > 85:
            worstcase = 2
            error_message = error_message + "\n ERROR: " + nodename + " - " + space + "% full"
            error_message = error_message + "\n\t" + node
    elif int(space) > 75:
            worstcase = 1
            error_message = error_message + "\n WARNING: " + nodename + " - " + space + "% full"
            error_message = error_message + "\n\t" + node
    if int(result) < int(worstcase):
            result = worstcase
    worstcase = 0

# Delete bash script file
os.remove(scriptfile)
# ----------------------------------------------------------------------------------------------------------------------
# UPDATE REPORT FILE
reportfile = open(reportdirectory + sys.argv[3] + '.txt', "a")              # Open the current report file
reportfile.write('TEST:         ' + sys.argv[1] + '\n')                     # Open test section in report file
reportfile.write('RESULT:       ' + config['framework']['errortypes'][result])  # Add test status to report
if result != 0:                                                             # Check if test wasn't successful
    errorfilename = sys.argv[3] + "_" + sys.argv[1]                         # Create a error_reportfile
    errorfile = open(reportdirectory + errorfilename + '.txt', "w+")        # Create error report file
    errorfile.write(test_data)                                              # Write error data to error file
    errorfile.close()                                                       # Close error file
    reportfile.write(" : " + error_message + '\n')                          # Add error message to report
    reportfile.write("\tPlease look at [" + errorfilename + ".txt] for further details.")
reportfile.write('\n' + config['framework']['formatting']['linebreak'] + '\n')  # Add line break to report file per test
reportfile.close()  # Close report file
# ----------------------------------------------------------------------------------------------------------------------
# ADD CURRENT TEST RESULT TO OVERALL REPORT STATUS
statusfile = open(rootpath + "/workingstatus", "r")
current_status = int(statusfile.read())
statusfile.close()
#import ipdb; ipdb.set_trace()
if current_status < result:
    statusfile = open(rootpath + "/workingstatus", "w")
    statusfile.truncate(0)
    statusfile.write(str(result))
    statusfile.close()

