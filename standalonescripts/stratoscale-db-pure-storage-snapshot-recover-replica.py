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


#!{sys.executable} -m pip install purestorage
#!{sys.executable} -m pip install pyyaml


# In[3]:


print(u"[INIT] Initialising script.").encode('utf-8')
# Configure environment
tz_utc = pytz.timezone("UTC") # Set timezone for data source
current_day= ["ISO Week days start from 1","Mon","Tues","Wed","Thurs","Fri","Sat","Sun"]
rootpath = os.path.dirname(os.path.realpath('__file__'))  # Get the root path


# In[4]:


# Import config file data
with open(rootpath + '/config.yml', 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        print(u" [\u2713] Config file loaded.").encode('utf-8')
    except yaml.YAMLError as exc:
        print(u" [\u2717] Could not load the config file.").encode('utf-8')
        print(exc)
        exit()


# In[5]:


try:
    dbs_id = raw_input(" [>] Please input the database ID for the database you wish to recover a new DB from: ").lower()
    dbs_name_replica = raw_input(" [>] Please input a name for the Replica database: ").lower()
    dbs_parameter_group_id_replica = raw_input(" [>] Please input the ID of the paramater group to be attached: ").lower()
    dbs_master_password = raw_input(" [>] Please input the master user password for the db: ").lower()
except:
    print(u" [\u2717] Failed to collect the input data. Please try again.").encode('utf-8')
    exit()


# In[6]:


print(u"[>] SOURCE DB").encode('utf-8') 
# Configure Stratoscale API connection (Source Region)
symp_url = "https://" + config["region_access"]["ipaddress"]
symp_domain = config["region_access"]["cloud_domain"]
symp_user = config["region_access"]["cloud_user"]
symp_password = config["region_access"]["cloud_password"]
symp_cloud_admin_password = config["region_access"]["cloud_admin_password"]
symp_project = config["region_access"]["project"]

my_session = requests.Session()
my_admin_session = requests.Session()
my_session.verify = False
my_admin_session.verify = False

try:
    client = symphony_client.Client(url=symp_url, session=my_session)
    client_login = client.login(domain=symp_domain, username=symp_user, password=symp_password,project=symp_project)
    print(u" [\u2713] Stratoscale user region [{}] session established.".format(symp_url)).encode('utf-8')
except:
    print(u" [\u2717] Could not connect to the Stratosacle region [{}] as user".format(symp_url)).encode('utf-8')
    exit()

try:
    client_admin = symphony_client.Client(url=symp_url, session=my_admin_session)
    client_admin_login = client_admin.login(domain="cloud_admin", username="admin", password=symp_cloud_admin_password,project="default")
    print(u" [\u2713] Stratoscale cloud admin region [{}] session established.".format(symp_url)).encode('utf-8')
except:
    print(u" [\u2717] Could not connect to the Stratosacle region [{}] as cloud admin".format(symp_url)).encode('utf-8')
    exit()


# In[7]:


# Collect SOURCE DB data
print(u"[SOURCE DB] Collecting information from original DB [{}].".format(dbs_id)).encode('utf-8')
database=client.dbs.instance.get(dbs_id)
# Environmentals
dbs_vpc_id = client.vpcs.list()[0].get("id")
print(u" [\u2713] VPC ID\t\t\t\t> {}".format(dbs_vpc_id)).encode('utf-8')
dbs_storage_pool_id = client.melet.pools.get_default()
print(u" [\u2713] Storage Pool ID (Default)\t\t> {}".format(dbs_storage_pool_id)).encode('utf-8')
# Get Database Metadata
dbs_original_name = database.get("name")
print(u" [\u2713] Source DB Name\t\t\t> {}".format(dbs_original_name)).encode('utf-8')
dbs_engine_version_id = database.get("engine_version_id")
engines = client.dbs.engines.versions.list()
for engine in engines:
    if (engine.id == dbs_engine_version_id):
        dbs_engine_build = engine.name
        dbs_engine_name = engine.enabled_revision.engine_name
print(u" [\u2713] Source DB Engine Version ID\t> {}".format(dbs_engine_version_id)).encode('utf-8')
print(u" [\u2713] Source DB Engine Version\t\t> {} {}".format(dbs_engine_name, dbs_engine_build)).encode('utf-8')
dbs_network_id = database.get("network_id")
print(u" [\u2713] Source DB Network ID\t\t> {}".format(dbs_network_id)).encode('utf-8')
dbs_master_username = database.get("master_user_name")
print(u" [\u2713] Source DB Master Username\t\t> {}".format(dbs_master_username)).encode('utf-8')
dbs_master_db_name = database.get("db_name")
print(u" [\u2713] Source DB Master DB Name\t\t> {}".format(dbs_master_db_name)).encode('utf-8')
dbs_instance_type = database.get("instance_type")
print(u" [\u2713] Source DB Instance Type\t\t> {}".format(dbs_instance_type)).encode('utf-8')
dbs_project_id = database.get("project_id")
print(u" [\u2713] Source DB Instance Project ID\t> {}".format(dbs_project_id)).encode('utf-8')
dbs_parameter_group_id = database.get("parameter_group_id")
print(u" [\u2713] Source DB Parameter Group ID\t> {}".format(dbs_parameter_group_id)).encode('utf-8')
source_parameter_group = client.dbs.parameter_group.get(dbs_parameter_group_id)
dbs_security_group_id = database.get("security_group_id")
print(u" [\u2713] Source DB Security Group ID\t> {}".format(dbs_security_group_id)).encode('utf-8')
db_elastic_ip_address = database.floating_ip
print(u" [\u2713] Source elastic IP address\t\t> {}".format(db_elastic_ip_address)).encode('utf-8')
db_access_port = database.ports
print(u" [\u2713] Source access port is\t\t> {}".format(db_access_port)).encode('utf-8')
db_vm_data_vol_id = client.vms.get(database.vm_id).get("volumes")[0]
print(u" [\u2713] Source DB Volume ID\t\t> {}".format(db_vm_data_vol_id)).encode('utf-8')


# In[8]:


# Disconnect source region, connect to replication region
client.logout()
client_admin.logout()


# In[9]:


print(u"[>] REPLICA DB").encode('utf-8') 
# Configure Stratoscale API connection (Source Region)
symp_url = "https://" + config["region_access_replicasite"]["ipaddress"]
symp_domain = config["region_access_replicasite"]["cloud_domain"]
symp_user = config["region_access_replicasite"]["cloud_user"]
symp_password = config["region_access_replicasite"]["cloud_password"]
symp_cloud_admin_password = config["region_access_replicasite"]["cloud_admin_password"]
symp_project = config["region_access_replicasite"]["project"]

my_session = requests.Session()
my_admin_session = requests.Session()
my_session.verify = False
my_admin_session.verify = False

try:
    client = symphony_client.Client(url=symp_url, session=my_session)
    client_login = client.login(domain=symp_domain, username=symp_user, password=symp_password,project=symp_project)
    print(u" [\u2713] Stratoscale user region [{}] session established.".format(symp_url)).encode('utf-8')
except:
    print(u" [\u2717] Could not connect to the Stratosacle region [{}] as user".format(symp_url)).encode('utf-8')
    exit()

try:
    client_admin = symphony_client.Client(url=symp_url, session=my_admin_session)
    client_admin_login = client_admin.login(domain="cloud_admin", username="admin", password=symp_cloud_admin_password,project="default")
    print(u" [\u2713] Stratoscale cloud admin region [{}] session established.".format(symp_url)).encode('utf-8')
except:
    print(u" [\u2717] Could not connect to the Stratosacle region [{}] as cloud admin".format(symp_url)).encode('utf-8')
    exit()


# In[10]:


# Configuring parameters for new DB
print("[NEW DB DEPLOYMENT] Finalizing new DB.").encode('utf-8')
print(u" [\u2713] A new DB called [{}] will be created from data in the DB [{}].".format(
    dbs_name_replica,
    dbs_original_name
)).encode('utf-8')
answer = raw_input(" [>] Please type \"confirm\" to create the DB: ").lower()
if answer != "confirm":
    print(u" [\u2717] Process Cancelled - Nothing will be done.").encode('utf-8')
    exit()


# In[11]:


#Configure Pure Storage API Connection
pureip = str(config['purestoragearray_replicasite']['ipaddress'])
puretoken = str(config['purestoragearray_replicasite']['apitoken'])
array = purestorage.FlashArray(pureip, api_token=puretoken)
try:
    array_info = array.get()
    print(u" [\u2713] FlashArray {} [{}] (version {}) REST session established!".format(array_info['array_name'],
                                                                                pureip, array_info['version'])).encode('utf-8')
except:
    print(u" [\u2717] Could not connect to the Pure Storage array - IP [" + pureip + "]").encode('utf-8')
    exit()


# In[12]:


# Generating the data volume and import to Stratoscale
volumename = "tempvolume-delete"
try: 
    array.destroy_volume(volumename)
    array.eradicate_volume(volumename)
except:
    print(u" [?] Attempted a clean of old volume. Not needed.").encode('utf-8')
    
try:
    snapshots = array.get_volume("volume-" + db_vm_data_vol_id + "-cinder", snap="True")
    response = array.copy_volume(snapshots[0].get("name"), volumename)
    print(u" [\u2713] Creating a volume from selected recovery point (snapshot) on the Pure Storage Array. NAME [{}]".format(volumename)).encode('utf-8')
except:
    print(u" [\u2717] Could not create a volume on the Pure Storage Array. Please try again.").encode('utf-8')
    exit()


# In[13]:


# Import volume for use in Stratoscale
try:
    response = client_admin.meletvolumes.manage(name="{} - Data".format(dbs_name_replica), 
                           storage_pool=dbs_storage_pool_id,
                           reference = {"name" : volumename},
                           description="A restored Data volume for {}".format(dbs_name_replica),
                           project_id=dbs_project_id
                          )
    volume_id = response.get("id")
    print(u" [\u2713] The volume [{}] was imported into Stratosacle and renamed to [{}]. ID [{}]".format(volumename, "{} - Data".format(dbs_name_replica), volume_id)).encode('utf-8')
except:
    try:
        array.destroy_volume(volumename)
        array.eradicate_volume(volumename)
    except:
        print(u" [\u2717] Could not remove the volume. It may not exist.").encode('utf-8')
    print(u" [\u2717] Could not import the volume. Please try again.").encode('utf-8')
    exit()


# In[14]:


# Collect Replica DB data
print(u"[REPLICA DB] Building metadeta for replica DB[{}].".format(dbs_id)).encode('utf-8')
### GET DB ENGINE VERSION
dbs_engine_version_id = "[notfound]"
engines = client.dbs.engines.versions.list()
for engine in engines:
    if dbs_engine_name == engine.enabled_revision.engine_name:
        if (dbs_engine_build == engine.name):
            dbs_engine_version_id = engine.id
if (dbs_engine_version_id == "[notfound]"):
    print(u" [\u2717] The engine build is not active/found for use.").encode('utf-8')
    exit()
print(u" [\u2713] Replica DB Engine Version ID\t> {}".format(dbs_engine_version_id)).encode('utf-8')
print(u" [\u2713] Replica DB Name\t\t\t> {}".format(dbs_name_replica)).encode('utf-8')
dbs_storage_pool_id = client.melet.pools.get_default()
print(u" [\u2713] Storage Pool ID (Default)\t\t> {}".format(dbs_storage_pool_id)).encode('utf-8')
for network in client.vpcs.networks.list():
    if network.is_default:
        dbs_network_new = network
dbs_network_id_replica = dbs_network_new.id
print(u" [\u2713] Replica DB Network ID\t\t> {}".format(dbs_network_id_replica)).encode('utf-8')
print(u" [\u2713] Replica DB Master Username\t\t> {}".format(dbs_master_username)).encode('utf-8')
print(u" [\u2713] Replica DB Master Password\t\t> {}".format(dbs_master_password)).encode('utf-8')
print(u" [\u2713] Replica DB Instance Type\t\t> {}".format(dbs_instance_type)).encode('utf-8')
print(u" [\u2713] Replica DB Volume ID\t\t> {}".format(volume_id)).encode('utf-8')
print(u" [\u2713] Replica DB Parameter Group ID\t> {}".format(dbs_parameter_group_id_replica)).encode('utf-8')
print(u" [\u2713] Master DB access IP\t\t> {}".format(db_elastic_ip_address)).encode('utf-8')
print(u" [\u2713] Master DB access port\t\t> {}".format(db_access_port)).encode('utf-8')
     
### MVP2 - ASK FOR CUSTOM IP ADDRESS MVP2
### MVP2 - COPARE PARAMETER GROUPS THAT ARE SELECTED


# In[15]:


# Build up bash query (creating replica does not exist in this build)
cli_string = "symp -k -d \'{}\' -u \'{}\' -r \'{}\' -p \'{}\' dbs instance create \'{}\' \'{}\' \'{}\' \'{}\' \'{}\' \'{}\' \'{}\' --volume-id \'{}\' --param-group-id \'{}\' --replication-host \'{}\' --replication-port \'{}\' --is-external".format(
    symp_domain,
    symp_user,
    symp_project,
    symp_password,    
    dbs_engine_version_id,
    dbs_name_replica,
    dbs_storage_pool_id,
    dbs_network_id_replica,
    dbs_master_username,
    dbs_master_password,
    dbs_instance_type,
    volume_id,
    dbs_parameter_group_id_replica,
    db_elastic_ip_address,
    db_access_port
)
print u"[>] {} STRING TO RUN: ".format(cli_string)


# In[16]:


print(u"[>] Attempting DB creation.").encode('utf-8')
try:
    os.system(cli_string)
except:
    print(u" [\u2717] Could not run the shell request.").encode('utf-8')


# In[17]:


# Disconnect sessions
array.invalidate_cookie()
# Disconnect source region, connect to replication region
client.logout()
client_admin.logout()


# In[18]:


#dbs instance create 
#[engine_version_id] 
#["db name"] 
#[storage_pool_id] 
#[network_id] 
#["master_user_name"] 
#["master_user_password"] 
#["instance_type"] 
#--volume-id [new-replicated-volume-id]
#--param-group-id [parameter-group-id]
#--replication-host ["ip address of master"] 
#--replication-port ["db data port of master"] 
#--fip-id [id of elastic IP] 
#--is-external

