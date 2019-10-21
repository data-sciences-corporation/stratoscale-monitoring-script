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
#   This module checks the database volume utilisation.                                                                #
#                                                                   exi                                                   #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# CHANGELOG                                                                                                            #
# v1.0 - 29 March 2019 (Richard Raymond)                                                                               #
#   - Initial version                                                                                                  #
#       Source: 00-template.py [0.4] - Requires: monitor.py [v0.5]                                                     #
# v1.1 - 10 April 2019 (Richard Raymond)                                                                               #
#   - Several bug fixes                                                                                                #
# v1.2 - 21 October 2019 (Richard Raymond)                                                                             #
#   - Script rewritten to accommodate removal of GCM tool as well as addition of metrics by symp client.               #
#                                                                                                                      #
########################################################################################################################

# MODULES
import sys
import yaml
import requests
import symphony_client


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
testdirectory = rootpath + "/" + config['framework']['directory']['test'] + "/"  # Generate dir for test
reportdirectory = rootpath + "/" + config['framework']['directory']['report'] + "/"  # Generate dir for reports
workingdirectory = rootpath + "/" + config['framework']['directory']['working'] + "/"  # Generate dir for working dir
scriptdirectory = rootpath + "/" + config['framework']['directory']['script'] + "/"  # Generate dir for sub scripts

# SCRIPT VARIABLES
result = 0  # Initialize OK marker
error_message = "Some DB data volumes are nearly full. Please extend them.\n"  # Error message to provide overview
test_data = ""  # Full error contents

# README.txt = scriptdirectory + sys.argv[1] + ".sh"                        # Create a script file
# ----------------------------------------------------------------------------------------------------------------------
worstcase = 0
# Connect to Symphony
symp_domain = config['region']['region1']['sympaccount']
symp_user = config['region']['region1']['sympusername']
symp_password = config['region']['region1']['symppassword']
symp_project = "default"
symp_url = "https://" + config['region']['region1']['ipaddress']
symp_insecure = True
symp_certfile = "None"
my_session = requests.Session()
my_session.verify = False
try:
    client = symphony_client.Client(url=symp_url, session=my_session)
    client_login = client.login(domain=symp_domain, username=symp_user, password=symp_password, project=symp_project)
except:
    print("Could not connect to the Stratosacle region [{}]".format(symp_url))
    error_message = "Could not connect to symphony region."
    result = 1
if result < 1:
    class textCol:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        PURPLE = '\033[95m'
        CYCAN = '\033[96m'
        END = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    dbs = client.dbs.instance.list()
    count = 0
    for db in dbs:
        worstcase = 0
        count = count + 1
        if db.status.lower() == "active":
            status = "{}[Active]".format(textCol.GREEN)
        elif db.status.lower() == "pending":
            status = "{}[Pending]".format(textCol.PURPLE)
        elif db.status.lower() == "processing":
            status = "{}[Processing]".format(textCol.CYCAN)
        elif db.status.lower() == "stopped":
            status = "{}[Stopped]".format(textCol.BLUE)
        else:
            status = "{}[Error]".format(textCol.RED)
        db_details = (" [{}] {}{} [{}]{}\n  DB ID {}\t{}{}\n".format(
            count,
            textCol.BOLD,
            db.name,
            db.floating_ip,
            textCol.END,
            db.id,
            status,
            textCol.END
        ))
        db_data = client.dbs.instance.get(db.id)
        try:
            percent_used = 100 - int(db_data.stats.get("df/percent_bytes__free"))
            if percent_used > 85:
                percent_used = "{}{}[CRITICAL] - {}".format(textCol.BOLD, textCol.RED, percent_used)
                worstcase = 3
            elif percent_used > 80:
                percent_used = "{}[ERROR] - {}".format(textCol.PURPLE, percent_used)
                worstcase = 2
            elif percent_used > 70:
                percent_used = "{}[WARNING] - {}".format(textCol.YELLOW, percent_used)
                worstcase = 1
            else:
                percent_used = "{}[OK] - {}".format(textCol.GREEN, percent_used)
                worstcase = 0
        except:
            percent_used = "{}[No Data] - ?".format(textCol.YELLOW)
            worstcase = 1
        capacity_details = "  Data Volume\t\t\t\t\t{}% consumed of the allocated {}GB{}\n".format(
            percent_used,
            db.allocated_storage,
            textCol.END
        )
        print("{}{}".format(db_details, capacity_details))
        if int(result) < int(worstcase):
            result = worstcase
        test_data = "{}{}{}".format(test_data, db_details, capacity_details)
        if worstcase > 0:
            error_message = "{}{}{}".format(error_message, db_details, capacity_details)

# Clean special characters out of text data
error_message = error_message.replace(textCol.RED, '')
error_message = error_message.replace(textCol.GREEN, '')
error_message = error_message.replace(textCol.YELLOW, '')
error_message = error_message.replace(textCol.BLUE, '')
error_message = error_message.replace(textCol.PURPLE, '')
error_message = error_message.replace(textCol.CYCAN, '')
error_message = error_message.replace(textCol.END, '')
error_message = error_message.replace(textCol.BOLD, '')
error_message = error_message.replace(textCol.UNDERLINE, '')

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
statusfile = open(rootpath + "/workingstatus", "r")
current_status = int(statusfile.read())
statusfile.close()
# import ipdb; ipdb.set_trace()
if current_status < result:
    statusfile = open(rootpath + "/workingstatus", "w")
    statusfile.truncate(0)
    statusfile.write(str(result))
    statusfile.close()
