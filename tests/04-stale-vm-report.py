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
#   This module is for checking for potential reclaimable vms.                                                         #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# CHANGELOG                                                                                                            #
# v1.0 - 04 April 2019 (Richard Raymond)                                                                               #
#   - Initial version                                                                                                  #
# v1.1 - 05 April 2019 (Richard Raymond)                                                                               #
#   - Fixed proxy issue when connecting to Symphony using python modules.                                              #
#   - Updated list of VMs to better handle html format emails.                                                         #
#                                                                                                                      #
########################################################################################################################

# MODULES
import sys
import yaml
import requests
import symphony_client
from datetime import datetime


# DEFINITIONS
def create_symp_client(i_url, i_domain, i_username, i_password, i_project, i_insecure, i_cert_file=None):
    my_session = requests.Session()
    # disable Proxy
    my_session.trust_env = False
    if i_insecure is True:
        my_session.verify = False
    elif i_cert_file is not None:
        my_session.cert = i_cert_file
    sympclient = symphony_client.Client(url=i_url, session=my_session)
    sympclient.login(domain=i_domain, username=i_username, password=i_password,
                     project=i_project)
    return sympclient


# PARAMETERS
# 1 - Script name, 2 - Root path of calling script, 3 - Report filename

# CONFIG VARIABLES
rootpath = sys.argv[2]
config = yaml.load(open(rootpath + '/config.yml', 'r'))  # Pull in config information from YML file.
johntestdirectory = rootpath + "/" + config['framework']['directory']['test'] + "/"  # Generate dir for test
reportdirectory = rootpath + "/" + config['framework']['directory']['report'] + "/"  # Generate dir for reports
workingdirectory = rootpath + "/" + config['framework']['directory']['working'] + "/"  # Generate dir for working dir
scriptdirectory = rootpath + "/" + config['framework']['directory']['script'] + "/"  # Generate dir for sub scripts

# SCRIPT VARIABLES
result = 1  # Initialize WARN (this test does not fail)
error_message = "VM/s could possibly be cleaned."  # Error message to provide overview
test_data = ""  # Full error contents

# scriptfile = scriptdirectory + sys.argv[1] + ".sh"                        # Create a script file
# ----------------------------------------------------------------------------------------------------------------------

# Connect to Symphony
symp_domain = config['region']['region1']['sympaccount']
symp_user = config['region']['region1']['sympusername']
symp_password = config['region']['region1']['symppassword']
symp_project = "default"
symp_url = "https://" + config['region']['region1']['ipaddress']
symp_insecure = True
symp_certfile = "None"
client = create_symp_client(symp_url, symp_domain, symp_user, symp_password, symp_project, symp_insecure, symp_certfile)

# Get List of active DBs
test_data = [db for db in client.vms.list() if db['status'] == 'shutoff']
vms = [[vm['id'], vm['name'], vm['updated']] for vm in test_data]
error_message = error_message + "\n Last Modified".ljust(35) + "  VM ID".ljust(50) + "  VM Name".ljust(30)
error_message = error_message + "\n  ----------- ".ljust(35) + "   --- ".ljust(50) + "   ----- ".ljust(30)
for vm in vms:
    time = datetime.strptime(str(vm[2]), '%Y-%m-%dT%H:%M:%SZ')
    time_between_insertion = datetime.now() - time
    if time_between_insertion.days > 30:
        error_message = error_message + "\n " + str(time).ljust(35) + str(vm[0]).ljust(50) + str(vm[1]).ljust(30)
if len(error_message) < 1:
    result = 0
# import ipdb; ipdb.set_trace()

test_data = str(test_data)
# ----------------------------------------------------------------------------------------------------------------------
# UPDATE REPORT FILE
reportfile = open(reportdirectory + sys.argv[3] + '.txt', "a")  # Open the current report file
reportfile.write('TEST:         ' + sys.argv[1] + '\n')  # Open test section in report file
reportfile.write('RESULT:       ' + config['framework']['errortypes'][result])  # Add test status to report
if result != 0:  # Check if test wasn't successful
    errorfilename = sys.argv[3] + "_" + sys.argv[1]  # Create a error_reportfile
    errorfile = open(reportdirectory + errorfilename + '.txt', "w+")  # Create error report file
    errorfile.write(test_data)  # Write error data to error file
    errorfile.close()  # Close error file
    reportfile.write(" : " + error_message + '\n')  # Add error message to report
    reportfile.write("\tPlease look at [" + errorfilename + ".txt] for further details.")
reportfile.write('\n' + config['framework']['formatting']['linebreak'] + '\n')  # Add line break to report file per test
reportfile.close()  # Close report file
# ADD CURRENT TEST RESULT TO OVERALL REPORT STATUS
statusfile = open(rootpath + "/currentstatus", "r")
current_status = int(statusfile.read())
statusfile.close()
#import ipdb; ipdb.set_trace()
if current_status < result:
    statusfile = open(rootpath + "/currentstatus", "w")
    statusfile.truncate(0)
    statusfile.write(str(result))
    statusfile.close()