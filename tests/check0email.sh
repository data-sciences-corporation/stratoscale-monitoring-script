#!/bin/bash
status="$(cat currentstatus)"
if [ "$status" == "0" ]
then
	python /root/tmp/StratoMonitor/sendtheemail.py
fi
