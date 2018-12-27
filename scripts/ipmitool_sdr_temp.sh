#!/usr/bin/bash

WORKDIR=$1
consul exec ipmitool sdr list | grep degrees | awk '{gsub(":","|"); print}' | sort -u > $WORKDIR"ipmitool_sdr_temp.out"
