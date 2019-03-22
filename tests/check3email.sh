#/!bin/bash
status="$(cat currentstatus)"
if [ "$status" == "3" ]
then
	python /root/tmp/StratoMonitor/sendtheemail.py
fi
