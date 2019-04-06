#!/bin/bash
status="$(cat currentstatus)"
if [[ "$status" == "2" ]]
then
	python /root/StratoMonitor/sendtheemail.py
fi
