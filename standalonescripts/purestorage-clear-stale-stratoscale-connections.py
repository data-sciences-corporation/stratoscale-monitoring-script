#!/usr/bin/env python
# coding: utf-8

import yaml  # For reading the config file
import os  # For path tools
import requests  # For symphony client
import symphony_client  # For connecting to Symphony region
import purestorage  # For running Pure Storage commands
import pytz  # To add timezone to datetime

#pip install purestorage
#pip install pyyaml

print(u"[INIT] Initialising script.")
# Configure environment
tz_utc = pytz.timezone("UTC") # Set timezone for data source
current_day= ["ISO Week days start from 1","Mon","Tues","Wed","Thurs","Fri","Sat","Sun"]
rootpath = os.path.dirname(os.path.realpath('__file__'))  # Get the root path

# Import config file data
with open(rootpath + '/config.yml', 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        print(u" [\u2713] Config file loaded.")
    except yaml.YAMLError as exc:
        print(u" [\u2717] Could not load the config file.")
        print(exc)
        exit()

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
    client_login = client.login(domain=symp_domain, username=symp_user, password=symp_password,project=symp_project)
    print(u" [\u2713] Stratoscale user region [{}] session established.".format(symp_url))
except:
    print(u" [\u2717] Could not connect to the Stratosacle region [{}] as user".format(symp_url))
    exit()

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

# Get hostname list
the_hosts = []
host_dict = {
    u'stratoshortname' : "empty",
    u'stratolongname' : "empty",
    u'pure' : "empty",
    u'vols' : []
}
array_hosts = array.list_hosts()
strato_hosts = client.nodes.list()
for strato_host in strato_hosts:
    for array_host in array_hosts:
        if strato_host.name in array_host.get("name"):
            print(" > found [{}]".format(strato_host.name))
            host_dict[u'stratoshortname'] = strato_host.name
            host_dict[u'stratolongname'] = strato_host.hostname
            host_dict[u'pure'] = array_host.get("name")
            hostvolumelist = array.list_host_connections(array_host.get("name"))
            host_dict[u'vols'] = []
            for hostvolume in hostvolumelist:
                host_dict[u'vols'].append(hostvolume.get("vol"))
            the_hosts.append(dict(host_dict))

print("Get which volumes are currently on which hosts.")
the_vols = []
vol_dict = {
    u'vol_id' : "empty",
    u'stratolongname' : "empty",
}

strato_volumes = client.meletvolumes.list()
for strato_volume in strato_volumes:
    try:
        strato_volume_host = strato_volume.attachedHost[0]
    except:
        strato_volume_host = "None"
    vol_dict[u'vol_id'] = "volume-{}-cinder".format(strato_volume.id)
    vol_dict[u'stratolongname'] = strato_volume_host
    the_vols.append(dict(vol_dict))

print("Compare Stratoscale volume connections to pure volume connections, and remove incorrect connections.")
for vol in the_vols:
    print(" {} [{}]".format(vol.get("vol_id"),vol.get("stratolongname")))
    for host in the_hosts:
        if host.get("stratolongname") == vol.get("stratolongname"):
            print("\tVolume should exist on this host [{}]".format(host.get("stratolongname")))
        else:
            if vol.get("vol_id") in host.get("vols"):
                print("\tDisconnecting volume from {}".format(host.get("stratolongname")))
                print("\t\t> {}\n\t\t> {}".format(host.get("pure"),vol.get("vol_id")))
                array.disconnect_host(host.get("pure"),vol.get("vol_id"))

# Disconnect sessions
array.invalidate_cookie()

