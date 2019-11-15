# !/usr/bin/python3
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
# v2.0 - 14 November 2019 (Ricardo Aguiar)                                                                             #
#   - Code rewritten, now uses SEL along with SDR                                                                      #
#                                                                                                                      #
########################################################################################################################

# Imports
import sys
import os
import yaml

# Root path
ROOT_PATH = os.getcwd()


# ----------------------------------------------------------------------------------------------------------------------
# Load Config and assign constants
def load_config():
    try:
        with open('{}/config.yml'.format(ROOT_PATH)) as config_raw:
            try:
                config = yaml.safe_load(config_raw)
            except yaml.YAMLError as E:
                print('Unable to load config:\n{}\nExiting...'.format(E))
                sys.exit()
    except IOError as E:
        print('Unable to open config:\n{}\nExiting...'.format(E))
        sys.exit()

    test_directory = '{}/{}/'.format(ROOT_PATH, config['framework']['directory']['test'])
    report_directory = '{}/{}/'.format(ROOT_PATH, config['framework']['directory']['report'])
    working_directory = '{}/{}/'.format(ROOT_PATH, config['framework']['directory']['working'])
    script_directory = '{}/{}/'.format(ROOT_PATH, config['framework']['directory']['script'])

    return test_directory, report_directory, working_directory, script_directory, config


TEST_DIRECTORY, REPORT_DIRECTORY, WORKING_DIRECTORY, SCRIPT_DIRECTORY, CONFIG = load_config()


# ----------------------------------------------------------------------------------------------------------------------
# Run IPMI checks
def run_checks():
    print('')
    sdr_problems = list()
    sel_problems = list()
    # List of what to ignore in SDR response
    valid_filter = ['finished', 'no reading', 'ok', 'completed / acknowledged']
    # Send a consul exec to identify members
    ping = os.popen("consul exec echo").read().split('\n')
    ping.pop()
    count_nodes = int(ping[-1][0])
    # Get Hardware Info
    sdr_output = os.popen("consul exec ipmitool sdr list").read().split('\n')
    sdr_output.pop()
    sel_output = os.popen("consul exec ipmitool sel list").read().split('\n')
    sel_output.pop()
    error_message = str()
    # Find Errors in Hardware Info
    for line in sdr_output:
        line = str(line)
        if not any(x in line for x in valid_filter):
            if line[-1] != ':':
                sdr_problems.append(line)
                error_message = '{}\nERROR: {}'.format(error_message, line)
    sel_counter = 0
    for line in sel_output:
        line = str(line)
        if 'SEL has no entries' in line:
            sel_counter += 1
    if sel_counter != count_nodes:
        for line in sel_output:
            line = str(line)
            if not any(x in line for x in valid_filter):
                if line[-1] != ':':
                    sel_problems.append(line)
                    error_message = '{}\nERROR: {}'.format(error_message, line)
    # Clear SEL to prevent false alerts from previous errors
    os.popen("consul exec ipmitool sel clear")
    test_data = str()
    # Write Errors to a String
    if sdr_problems:
        test_data = 'SDR Sensor Errors/Failures:\n' \
                    '{}\n\n'.format('\n'.join(sdr_problems))
        result = 2
    if sel_problems:
        test_data = '{}SEL Health Errors/Failures:\n' \
                    '{}'.format(test_data, '\n'.join(sel_problems))
        result = 2

# ----------------------------------------------------------------------------------------------------------------------
# UPDATE REPORT FILE
    report_file = open(REPORT_DIRECTORY + sys.argv[3] + '.txt', "a")              # Open the current report file
    report_file.write('TEST:         ' + sys.argv[1] + '\n')                     # Open test section in report file
    report_file.write('RESULT:       ' + CONFIG['framework']['errortypes'][result])  # Add test status to report
    if result != 0:                                                             # Check if test wasn't successful
        error_file_name = sys.argv[3] + "_" + sys.argv[1]                         # Create a error_reportfile
        error_file = open(REPORT_DIRECTORY + error_file_name + '.txt', "w+")        # Create error report file
        error_file.write(test_data)                                              # Write error data to error file
        error_file.close()                                                       # Close error file
        report_file.write(" : " + error_message + '\n')                          # Add error message to report
        report_file.write("\tPlease look at [" + error_file_name + ".txt] for further details.")
    # Add line break to report file per test
    report_file.write('\n{}\n'.format(CONFIG['framework']['formatting']['linebreak']))
    report_file.close()  # Close report file
# ----------------------------------------------------------------------------------------------------------------------
# ADD CURRENT TEST RESULT TO OVERALL REPORT STATUS
    status_file = open(ROOT_PATH + "/workingstatus", "r")
    current_status = int(status_file.read())
    status_file.close()
    # import ipdb; ipdb.set_trace()
    if current_status < result:
        status_file = open(ROOT_PATH + "/workingstatus", "w")
        status_file.truncate(0)
        status_file.write(str(result))
        status_file.close()


if __name__ == '__main__':
    sys.exit(run_checks())
