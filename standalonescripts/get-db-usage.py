#!/usr/bin/env python
# coding: utf-8
import yaml  # For reading the config file
import os  # For path tools
import requests  # For symphony client
import symphony_client  # For connecting to Symphony region
import pytz  # To add timezone to datetime

# get_ipython().system(u'{sys.executable} -m pip install pyyaml')

print(u"[INIT] Initialising script.")
# Configure environment
tz_utc = pytz.timezone("UTC")  # Set timezone for data source
rootpath = os.path.dirname(os.path.realpath('__file__'))  # Get the root path

# Import config file data
with open(rootpath + '/config.yml', 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        print(u" [\u2713] Config file loaded.").encode('utf-8')
    except yaml.YAMLError as exc:
        print(u" [\u2717] Could not load the config file.").encode('utf-8')
        print(exc)
        exit()


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


# Configure Stratoscale API connection
symp_url = "https://" + config["region_access"]["ipaddress"]
symp_domain = config["region_access"]["cloud_domain"]
symp_user = config["region_access"]["cloud_user"]
symp_password = config["region_access"]["cloud_password"]
symp_project = config["region_access"]["project"],
my_session = requests.Session()
my_session.verify = False

try:
    client = symphony_client.Client(url=symp_url, session=my_session)
    client_login = client.login(domain=symp_domain, username=symp_user, password=symp_password, project=symp_project)
    print(u" [\u2713] Stratoscale user region [{}] session established.".format(symp_url)).encode('utf-8')
except:
    print(u" [\u2717] Could not connect to the Stratosacle region [{}] as user".format(symp_url)).encode('utf-8')
    exit()

dbs = client.dbs.instance.list()
count = 0
for db in dbs:
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
    db_details = "-------------------------------------------------------------------------------------------"
    db_details = ("{}\n [{}] {}{} [{}]{}\n  DB ID {}\t{}{}".format(
        db_details,
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
        elif percent_used > 80:
            percent_used = "{}[ERROR] - {}".format(textCol.PURPLE, percent_used)
        elif percent_used > 70:
            percent_used = "{}[WARNING] - {}".format(textCol.YELLOW, percent_used)
        else:
            percent_used = "{}[OK] - {}".format(textCol.GREEN, percent_used)
    except:
        percent_used = "{}[No Data] - ?".format(textCol.YELLOW)
    capacity_details = "  Data Volume\t\t\t\t\t{}% consumed of the allocated {}GB{}".format(
        percent_used,
        db.allocated_storage,
        textCol.END
    )
    print(db_details).encode('utf-8')
    print(capacity_details).encode('utf-8')
