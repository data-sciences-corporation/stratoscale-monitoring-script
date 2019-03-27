#!/usr/bin/bash
#
###
## Script to get storage consumption from DBAAS instances
## Support: Up to version 5.2.1.4 due to GCM SYMP API redaction in 5.2.2+
## v1.0 - Angus Young
## v1.1 - Richard Raymond, Liaz Kamper & John van der Veen
###
#

WORKDIR=$1
SYMP_DOMAIN=$2
SYMP_USER=$3
SYMP_PASSWORD=$4

### Get list of VM_ID's from ACTIVE DBS instances
DBS_INSTANCES=()
while IFS= read -r line; do
    DBS_INSTANCES+=( "$line" )
done < <(  symp -k -d $SYMP_DOMAIN -u $SYMP_USER -p $SYMP_PASSWORD dbs instance list -c vm_id -f value --filters '{"status": "active"}' )

### Query each instance for storage utilization
for hostid in ${DBS_INSTANCES[@]}; do
   printf "$hostid\t"
   TEST_GCM_CONNECTED=$( symp -q -k -d $SYMP_DOMAIN -u $SYMP_USER -p $SYMP_PASSWORD gcm guest list-connected -f value | grep $hostid )
   if [ -z "$TEST_GCM_CONNECTED" ]
   then
      printf "[NOTCONNECTED]\n"
   else
      symp -q -k -d $SYMP_DOMAIN -u $SYMP_USER -p $SYMP_PASSWORD gcm guest run -f value $hostid cmd.run --args "df -h --output=size,pcent,target /dev/vdb"
   fi
done