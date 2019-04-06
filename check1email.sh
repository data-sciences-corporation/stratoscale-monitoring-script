#!/bin/bash
status="$(cat currentstatus)"
if [[ "$status" == "1" ]]
then
	python /root/StratoMonitor/sendtheemail.py
fi
