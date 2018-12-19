Stratoscale Monitoring Script

Installation:
1. Copy entire [StratoMonitor] directory onto Stratoscale cluster.
2. Use cron job to run [monitor.py] at required interval.

Upgrades:
1. Backup and custom test script files.
2. Pull latest repo from the github repo.
3. Replace old [StratoMonitor] with latest pull.
4. Copy custom test scripts into "tests" directory.

New Custom Scripts:
1. Copy 00-template.py
2. Give the new filename the appropriate category number as well as a fairly descriptive test name.
        00 - TEMPLATE
        01 - HARDWARE
        02 - NETWORK
        03 - OS
        04 - SYPMHONY
        05 - AWS
        06 - KUBERNETES
3. Write the script in the allocated custom script location (leaving other paramaters as is.
4. Update the 'result', 'error_message' & 'error_data' as they are what are output into the report file and subsequent
 report data dump files.
5. Update the explanation of the script in the comments with the script's purpose as well as with the changelog,
 including your name (so after the fact trouble shooting can be streamlined).

Updating Custom Scripts:
 Refer to steps 3,4,5 of "New Custom Scripts"

Requirements:
1. Python 3.6+ (may run on older versions).
