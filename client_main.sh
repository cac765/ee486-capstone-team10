#!/bin/bash

######## Client Side Main Script for People Detection ########
#
# Author: Corey Cline
#
# Date: 03/14/21
# Description:
# The main bash script to be used for executing the image_people_detector.py
# script for people detection with the default settings.
#
############################################################################

edge=$(hostname)

python3 image_people_detector.py \
--modeldir tflite1/Sample_TFLite_model \
--ground-truth config/ground_truth.json \
--device-id $edge \
--broker-ip store1.iot.nau.edu \
--client-name $edge

