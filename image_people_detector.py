######## Pi-Camera Object Detection Using TensorFlow Trained Classifier ########
#
# Author:  Corey Cline
# Members: Evan Genuise
#          Sara Barraclough
#          Vitaliy Kolontayev
# Date: 02/20/2021
# Description:
# The primary script for the EE486 Capstone Team 10 - People Counting People
# This program uses a TensorFlow Lite model to perform object detection on a
# single real-time image. It draws boxes and scores around the objects of
# interest, performs a top-view translation that is a hard-coded calibration,
# and prints the new location data to the console. The user has to option to
# connect the device to an MQTT broker to publish the data to a topic, and there
# is also a preview option to show the input image from the camera as well as
# display steps of the detection and top view transformation process.
#
# This code is based off the EdjeElectronics Tutorial at:
# https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi
#
# The script has been modified to fit the specific needs of the Capstone Team
################################################################################

# Import packages
import os
import argparse
import cv2
import numpy as np
import sys
import time
import json
import logging
from threading import Thread
import importlib.util
from utils.mqtt_client import *
from utils.top_view_transform import *
from utils.camera_stream import *

# Initialize the logger for the program
logging.basicConfig( format='%(levelname)s: %(message)s', level=logging.INFO )

# Set the arguments for the script
parser = argparse.ArgumentParser()
parser.add_argument( '--modeldir', help='Folder the .tflite file is located in',
                    required=True)
parser.add_argument('--graph', help='Name of the .tflite file, if different \
                                     than detect.tflite',
                    default='detect.tflite')
parser.add_argument('--labels', help='Name of the labelmap file, if different \
                                      than labelmap.txt',
                    default='labelmap.txt')
parser.add_argument('--threshold', help='Minimum confidence threshold for \
                                         displaying detected objects',
                    default=0.5)
parser.add_argument('--resolution', help='Desired webcam resolution in WxH. \
                                        If the webcam does not support the \
                                        resolution entered, errors may occur.',
                    default='736x480')
parser.add_argument('--ground-truth', help='Name of the file that contains the \
                                        ground truth boxes for this device.',
                    default="ground_truth.json")
parser.add_argument('--device-id', help='Device name for the ground truths \
                                         JSON file',
                    default=None)
parser.add_argument('--show-display', help='Displays image output with cv2',
                    action='store_true')
parser.add_argument('--broker-ip', help='IP Address of the MQTT Broker. If no \
                                       IP is specified, MQTT will not be used.',
                    default=None)
parser.add_argument('--client-name', help='Name of the MQTT Client. Default is \
                                           TX1.',
                    default='TX1')
parser.add_argument('--topic', help='MQTT topic to publish data to. Default \
                                     topic is test/occupancy.',
                    default='test/occupancy')
parser.add_argument('--interval', help='Interval in seconds to publish \
                                       to MQTT topic. Default interval is 10s.',
                    default=10)

args = parser.parse_args()

MODEL_NAME = args.modeldir
GRAPH_NAME = args.graph
LABELMAP_NAME = args.labels
min_conf_threshold = float( args.threshold )
resW, resH = args.resolution.split('x')
imW, imH = int(resW), int(resH)
ground_truth = args.ground_truth
DEV_ID = args.device_id
show_display = args.show_display
broker_ip = args.broker_ip
client_name = args.client_name
mqtt_topic = args.topic
publish_interval = int( args.interval )

# Validate MQTT input arguments
if broker_ip == None:
    if mqtt_topic != "test/occupancy":
        raise Exception( "Must specify a broker_ip to publish to a topic. " + \
                         "Use --broker-ip argument to connect to a broker." )
    if client_name != "TX1":
        raise Exception( "Must specify a broker_ip for a client_name. "+ \
                         "Use --broker-ip argument to connect to a broker." )
    if publish_interval != 10:
        raise Exception( "Must specify a broker_ip to publish at a given " + \
                         "interval. Use --broker-ip argument to connect " + \
                         "to a broker." )

# Load ground truth data
if ground_truth:
    try:
        with open( ground_truth ) as file:
            ground_truths = json.load( file )
            if DEV_ID not in ground_truths.keys():
                raise Exception( "[-] Invalid Device ID for Ground Truth data" )
            source_truth = np.float32( ground_truths[DEV_ID]["source"] )
            dest_truth = np.float32( ground_truths[DEV_ID]["destination"] )
            transform_matrix = getTransformMatrix( source_truth, dest_truth )
    except Exception as error:
        logging.error( "Error collecting ground truth data." )
        print( error )
        exit(1)
    

# Import TensorFlow libraries
# If tflite_runtime is installed, import interpreter from tflite_runtime,
# else import from regular tensorflow
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter

# Get path to current working directory
CWD_PATH = os.getcwd()

# Path to .tflite file, which contains the model used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if labels[0] == '???':
    del(labels[0])

# Load the TensorFlow Lite model
interpreter = Interpreter( model_path=PATH_TO_CKPT )

interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# Initialize camera stream
camerastream = CameraStream( imW, imH )
logging.info( "Camera warming up ..." )
time.sleep(2)

# Define callback function for MQTT message callback
def on_message( client, userdata, message ):
    """Callback function for receiving messages."""
    msg = message.payload.decode( "utf-8" )
    edge.msg_queue.append( msg )
    logging.info( "\n\tTopic: {}\n\tMessage: {}\n\tRetained: {}".format(
                  message.topic,msg, message.retain ) )

    if ( message.retain == 1 ):
        logging.info( "This was a retained message." )

# Initialize MQTT Client if broker ip was specified
if broker_ip:
    edge = MQTTClient( broker_ip, client_name )
    edge.client.on_message = on_message
    edge.connect()
    edge.loop_start()
    edge.subscribe( "eecapstone/snapshot" )

recording = True
while recording:
    if broker_ip:
        # Wait infinitely for the UPDATE command to be received from the broker
        cmd_received = False
        while not cmd_received:
            # Check if the message queue has messages
            if len( edge.msg_queue ) > 0:
                # Grab the message from the queue
                incoming_msg = edge.msg_queue.pop()
                # Check if message was the UPDATE command, exit from the loop
                if incoming_msg == "UPDATE":
                    cmd_received = True
                    
        # Load the image from the stream and reset the command flag
        frame1 = camerastream.read()
        cmd_received = False

    # If no broker specified, take the snapshot now and continue
    else:
        frame1 = camerastream.read()

    # Acquire frame and resize to expected shape [1xHxWx3]
    frame = frame1.copy()
    #frame = cv2.flip( frame, -1 ) # Uncomment to flip image from camera stream
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

    # Retrieve detection results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
    scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
    #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

    # Track number of occupants/locations
    num_occupants = 0
    locations = []

    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(scores)):
        if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            ymin = int(max(1,(boxes[i][0] * imH)))
            xmin = int(max(1,(boxes[i][1] * imW)))
            ymax = int(min(imH,(boxes[i][2] * imH)))
            xmax = int(min(imW,(boxes[i][3] * imW)))

            cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

            # Draw label
            object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
            label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
            cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
            cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

            # Count for People and get their locations
            if ( object_name == "person" ):
                num_occupants += 1
                location = getLocation( (xmin, ymin), (xmax, ymax) )
                locations.append( location )

    # Perform actual top view translation if ground truth data given
    if ground_truth:
        new_locs = []
        for loc in locations:
            new_loc = transformCentroidLocation( loc, transform_matrix )
            new_locs.append( new_loc )
        locations = new_locs

    # Check for broker connection before publishing transformed locations
    if broker_ip:
        edge.publish( mqtt_topic, str(locations), qos=2, retain=False )
    # If no broker, stop recording
    else:
        recording = False

    print( "Occupant Locations: ", locations )

    # Check for display debugging
    if show_display:
        print( frame.shape )
        # Draw occupant number in corner of screen
        cv2.putText(frame, 'PEOPLE: {}'.format(num_occupants),(10,25),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
        displayImage( frame, title="frame" )

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

camerastream.stop()
print("Done")
