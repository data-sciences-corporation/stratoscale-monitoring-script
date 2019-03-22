#/!bin/bash
status="$(cat currentstatus)"
if [ "$status" == "2" ]
then
	python /root/tmp/StratoMonitor/sendtheemail.py
fi
