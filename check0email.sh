#!/bin/bash
status="$(cat currentstatus)"
if [[ "$status" == "0" ]]
then
	python /root/StratoMonitor/sendtheemail.py
fi
