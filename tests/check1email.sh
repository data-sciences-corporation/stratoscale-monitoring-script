#/!bin/bash
status="$(cat currentstatus)"
if [ "$status" == "1" ]
then
	python /root/tmp/StratoMonitor/sendtheemail.py
fi
