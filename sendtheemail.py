#!/usr/bin/python3
########################################################################################################################
#                                           Stratoscale - Email Script                                                 #
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
#   This module e-mails the latest report to the user.                                                                 #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# CHANGELOG                                                                                                            #
# v0.1 - 22 March 2019 (Richard Raymond & Manesh Naransammy)                                                           #
#   - Initial version                                                                                                  #
########################################################################################################################

# MODULES
import os  # For os modules
import yaml  # For reading the config file
import smtplib  # For emailing the report
import string  # For string things
import datetime

# CONFIG VARIABLES
rootpath = os.path.dirname(os.path.abspath(__file__))  # Get the root path
config = yaml.load(open(rootpath + '/config.yml', 'r'))  # Pull in config information from YML file

# READ OUT LATEST TEST RESULTS
reportfile = open(rootpath + '/latestreport.txt', "r")  # Open the report file
fullreport = reportfile.read()  # Read the report file (save for mail body)
reportfile.close()  # Close the report file for later editing.

# GET CRITICALITY
statusfile = open(rootpath + "/currentstatus", "r")  # Open the file which shows the region status
status = statusfile.read()  # Get the status from the file
statusfile.close()  # Close the file

# EMAIL TIME
regionname = config['region']['region1']['name']  # Pull region name from config file
SUBJECT = "Stratoscale Region: " + regionname  # Create first part of subject line
SUBJECT = SUBJECT + " - Monitoring Report [" + config['framework']['errortypes'][
    int(status)] + "] ["  # Create second part
SUBJECT = SUBJECT + str(datetime.datetime.now().strftime("%X")) + "]"
FROM = regionname + "@stratoscale.com"  # Create from address
text = fullreport  # Add report to email body
BODY = string.join((  # Join e-mail components for sending
    "From: %s" % FROM,
    "To: %s" % ",".join(config['region']['email']['recipients']),
    "Subject: %s" % SUBJECT,
    "",
    text
), "\r\n")
server = smtplib.SMTP(config['region']['email']['server'])  # Connect to email server from config file
server.sendmail(FROM, config['region']['email']['recipients'], BODY)  # Send email
server.quit()  # Disconnect from e-mail server
# Disconnect from e-mail server