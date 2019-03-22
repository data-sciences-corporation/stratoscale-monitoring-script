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
#   This module is for checking the hardware health status of the Stratoscale nodes                                    #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# CHANGELOG                                                                                                            #
# v1.0 - 24 December 2018 (Josef Bitschnau)                                                                            #
#   Source: 00-template.py [v0.3] - Requires: monitor.py [v0.4]                                                        #
#   - Initial version                                                                                                  #
# v1.1 - 22 March 2019 (Richard Raymond)                                                                               #
#   Source: 00-template.py [v0.4] - Requires: monitor.py [v0.5]                                                        #
#   - Updated script to use latest template (adds improved e-mail granularity), no changes to test code.               #
#                                                                                                                      #
########################################################################################################################

# MODULES
import sys
import yaml
import subprocess
import itertools

# PARAMETERS
# 1 - Script name, 2 - Root path of calling script, 3 - Report filename

# CONFIG VARIABLES
rootpath = sys.argv[2]
config = yaml.load(open(rootpath + '/config.yml', 'r'))                    # Pull in config information from YML file.
testdirectory = rootpath + "/" + config['framework']['directory']['test'] + "/"        # Generate dir for test
reportdirectory = rootpath + "/" + config['framework']['directory']['report'] + "/"    # Generate dir for reports
workingdirectory = rootpath + "/" + config['framework']['directory']['working'] + "/"  # Generate dir for working dir
scriptdirectory = rootpath + "/" + config['framework']['directory']['script'] + "/"    # Generate dir for sub scripts

# SCRIPT VARIABLES
result = 4                                                                  # Initialize OK/NOK marker
error_message = ""                                               # Error message to provide overview
test_data = ""                                                   # Full error contents

# scriptfile = scriptdirectory + sys.argv[1] + ".sh"                        # Create a script file
# ----------------------------------------------------------------------------------------------------------------------
# TEST SCRIPT DATA GOES HERE

# symproc1 = subprocess.Popen(['symp','-k','-d','cloud_admin','-u','admin','-p','R@ck@tt@ck-123','node','list','-c','name','--quiet'], stdout=subprocess.PIPE)
# symproc2 = subprocess.Popen(['awk','''{print $2}'''], stdin=symproc1.stdout, stdout=subprocess.PIPE)
# symproc3 = subprocess.Popen(['grep','-v','name'], stdin=symproc2.stdout, stdout=subprocess.PIPE)
# symproc1.stdout.close()
# symproc2.stdout.close()
# nodes, err1 = symproc3.communicate()
# rc1 = symproc3.returncode
# if rc1 != 0:
#     exit(err1)
# nodes = nodes.lstrip('\n').rstrip('\n')
# nodes = nodes.splitlines()

## ipmitool sdr list all
## ipmitool sdr list event
## ipmitool sensor [get]
## ipmitool sdr [get]

subprocess.call('sh {}ipmitool_sdr_temp.sh {}'.format(scriptdirectory, workingdirectory), shell=True)
# t_sdr = [['node', 'sensor', 'reading', 'status']]
with open('{}ipmitool_sdr_temp.out'.format(workingdirectory), 'r') as f:
    for line in itertools.islice(f, 0, None):
        # print(line.split('|')[0].strip().strip('\n'))
        test_data = line.strip().strip('\n')
        if line.split('|')[3].strip().strip('\n') != 'ok':
            # print(line.strip().strip('\n'))
            result = 3
            error_message += line.strip().strip('\n')
        else:
            result = 0
        # t_sdr.append(line.split('|'))
f.close()

# ----------------------------------------------------------------------------------------------------------------------
# UPDATE REPORT FILE
reportfile = open(reportdirectory + sys.argv[3] + '.txt', "a")              # Open the current report file
reportfile.write('TEST:         ' + sys.argv[1] + '\n')                     # Open test section in report file
reportfile.write('RESULT:       ' + config['framework']['errortypes'][result])  # Add test status to report
if result != 0:                                                             # Check if test wasn't successful
    errorfilename = sys.argv[3] + "_" + sys.argv[1]                         # Create a error_reportfile
    errorfile = open(reportdirectory + errorfilename + '.txt', "w+")        # Create error report file
    errorfile.write(test_data)                                             # Write error data to error file
    errorfile.close()                                                       # Close error file
    reportfile.write(" : " + error_message + '\n')                          # Add error message to report
    reportfile.write("\tPlease look at [" + errorfilename + ".txt] for further details.")
reportfile.write('\n' + config['framework']['formatting']['linebreak'] + '\n')  # Add line break to report file per test
reportfile.close()
# ----------------------------------------------------------------------------------------------------------------------
# ADD CURRENT TEST RESULT TO OVERALL REPORT STATUS
statusfile = open(rootpath + "/currentstatus", "r+")
if int(statusfile.read) > result:
    statusfile.write(str(result))
statusfile.close()
