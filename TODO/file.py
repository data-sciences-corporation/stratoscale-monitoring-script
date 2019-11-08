#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys  # For running system level commands
import yaml  # For reading the config file
import os  # For path tools
import requests  # For symphony client
import symphony_client  # For connecting to Symphony region
import purestorage  # For running Pure Storage commands
from pip._vendor.distlib.compat import raw_input
import datetime
from pytz import timezone
import pytz  # To add timezone to datetime


# In[2]:


#pip install purestorage')
#pip install pyyaml')


# In[3]:


print(u"[INIT] Initialising script.")
# Configure environment
tz_utc = pytz.timezone("UTC") # Set timezone for data source
current_day= ["ISO Week days start from 1","Mon","Tues","Wed","Thurs","Fri","Sat","Sun"]
rootpath = os.path.dirname(os.path.realpath('__file__'))  # Get the root path


# In[4]:


# Import config file data
with open(rootpath + '/config.yml', 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        print(u" [\u2713] Config file loaded.")
    except yaml.YAMLError as exc:
        print(u" [\u2717] Could not load the config file.")
        print(exc)
        exit()


# In[5]:


# Configure Stratoscale API connection
symp_url = "https://" + config["region_access"]["ipaddress"]
symp_domain = config["region_access"]["cloud_domain"]
symp_user = config["region_access"]["cloud_user"]
symp_password = config["region_access"]["cloud_password"]
symp_project = config["region_access"]["project"],

my_session = requests.Session()
my_admin_session = requests.Session()
my_session.verify = False
my_admin_session.verify = False

try:
    client = symphony_client.Client(url=symp_url, session=my_admin_session)
    client_login = client.login(domain=symp_domain, username=symp_user, password=symp_password,project=symp_project)
    print(u" [\u2713] Stratoscale cloud admin region [{}] session established.".format(symp_url))
except:
    print(u" [\u2717] Could not connect to the Stratosacle region [{}] as cloud admin".format(symp_url))
    exit()


# In[6]:


#Configure Pure Storage API Connection
pureip = str(config['purestoragearray']['ipaddress'])
puretoken = str(config['purestoragearray']['apitoken'])
array = purestorage.FlashArray(pureip, api_token=puretoken)
try:
    array_info = array.get()
    print(u" [\u2713] FlashArray {} [{}] (version {}) REST session established!".format(array_info['array_name'],
                                                                                pureip, array_info['version']))
except:
    print(u" [\u2717] Could not connect to the Pure Storage array - IP [" + pureip + "]")
    exit()


# In[13]:


# Iterate through each DB
dbs_storage_pool_id = client.melet.pools.get_default()
print(u"Storage Pool ID (Default) - [{}]\n".format(dbs_storage_pool_id))
for db in client.dbs.instance.list():
    try:
        db_id = db.id
        print(u"\n [>] DB\t\t\t\t {}.".format(db_id))
        database=client.dbs.instance.get(db_id)
        db_name = database.get("name")
        print(u" [\u2713] DB Name\t\t\t {}".format(db_name))
        db_vm_data_vol_id = client.vms.get(database.vm_id).get("volumes")[0]
        print(u" [\u2713] DB Volume ID\t\t {}".format(db_vm_data_vol_id))
                # Get snapshots
        snapshots = array.get_volume("volume-" + db_vm_data_vol_id + "-cinder", snap="True")
        if snapshots == []:
            print (u"  [\u2717] There are no snapshots the DB's data volume.")
        else:
            print (u"  [\u2713] Listing snapshots the DB's data volume.")
            count = 0
            for snapshot in snapshots:
                count = count + 1
                time_utc = datetime.datetime.strptime(snapshot.get("created"), "%Y-%m-%dT%H:%M:%SZ")
                time_utc = tz_utc.localize(time_utc, is_dst=None)
                snaptime = time_utc.astimezone(timezone("Africa/Johannesburg"))
                time = "{} [{}]".format(snaptime.strftime("%H:%M:%S %d/%m/%Y"),current_day[snaptime.isoweekday()])
                print("  [{}]\t{} \t{} ".format(str(count), time, snapshot.get("name")))
    except:
        print(u" [\u2717] There seems to be a problem with that DB")


# In[8]:


# Disconnect sessions
array.invalidate_cookie()


# In[9]:


array

