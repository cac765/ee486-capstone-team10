#!/bin/bash

######## Server Side Main Script for Automation of Data Collection ########
#
# Author: Corey Cline
#
# Date: 03/14/21
# Description:
# The main bash script to be used for executing the collect_people_data.py
# with the default settings.
#
############################################################################

python3 ~/repos/ee486-capstone-team10/server/collect_people_data.py \
--broker-ip store1.iot.nau.edu \
--client-name store1
