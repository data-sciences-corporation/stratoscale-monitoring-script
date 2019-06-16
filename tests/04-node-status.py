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
#   This module is for high level checking the node status.                                                            #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# CHANGELOG                                                                                                            #
# v1.0 - 24 December 2018 (Richard Raymond)                                                                            #
#   Source: 00-template.py [v0.4] - Requires: monitor.py [v0.4]                                                        #
#   - Initial version of the script                                                                                    #
# v1.1 - 22 March 2019 (Richard Raymond)                                                                               #
#   Source: 00-template.py [v0.4] - Requires: monitor.py [v0.5]                                                        #
#   - Updated script to use latest template (adds improved e-mail granularity), no changes to test code.               #
# v1.2 - 10 April 2019 (Richard Raymond)                                                                               #
#   - Several bug fixes                                                                                                #
#                                                                                                                      #
########################################################################################################################

# MODULES
import os
import sys
import yaml
import subprocess

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
error_message = "Node/s are unhealthy.\n"                                   # Error message to provide overview
test_data = "Node status\n"                                                 # Full error contents

tenant = config['region']['region1']['sympaccount']                         # Get symphony admin account
user = config['region']['region1']['sympusername']                          # Get symphony admin user
password = config['region']['region1']['symppassword']                      # Get symphony admin user password

scriptfile = scriptdirectory + sys.argv[1] + ".sh"                          # Create a script file
# ----------------------------------------------------------------------------------------------------------------------
# TEST SCRIPT DATA GOES HERE

# Make a bash script
bashscript = open(scriptfile, "w+")
accessdetails = '-d ' + tenant + ' -u ' + user + ' -p ' + password
bashscript.write("#!/bin/bash\nsymp -k " + accessdetails + ' ')
bashscript.write("node list -c name -c state -c state_fail_reasons -f yaml --quiet")
bashscript.close()

# Allow execute access
os.chmod(scriptfile, 0o755)                                                 # Force octal data type
process = subprocess.Popen(scriptfile, stdout=subprocess.PIPE)
output, error = process.communicate()

# Get data from script and import to yaml
response_yaml = yaml.load(output)
test_data = test_data + output

# Iterate through node list and check status
for i in range(len(response_yaml)):
    if response_yaml[i]['state'] != "active":
        result = 3
        error_message = error_message + '\t' + str(response_yaml[i]['name']) + ' is in state [' + str(response_yaml[i]['state'])
        error_message = error_message + '] - ' + str(response_yaml[i]['state_fail_reasons']) + '\n'
        #Sh*tty hack, because it's father's day.
    if response_yaml[i]['state'] == "in_maintenance":
        result = 1  # Set alert to warning
        error_message = error_message + '\t' + str(response_yaml[i]['name']) + ' is in state [' + str(response_yaml[i]['state'])
        error_message = error_message + '] - ' + str(response_yaml[i]['state_fail_reasons']) + '\n'

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
reportfile.close()
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
