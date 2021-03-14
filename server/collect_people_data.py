######## Server-Side Script for Data Collection and Storage ########
# 
# Authors: Corey Cline
#          Evan Genuise
#          Sara Barraclough
#          Vitaliy Kolontayev
#
# Date: 02/25/21
# Description:
# The primary script for the serer-side data processing of the EE486 Capstone
# Team 10 - People Counting People. This script uses MQTT Protocol to conduct
# two-way communication between the server device and multiple camera devices.
# Once the communication is established and data is collected, the server runs 
# the density clustering process to resolve double counting issues, and inserts
# the integer occupancy result into the SQL table for data storage.
# 
###############################################################################

# Standard library imports
import sys
import argparse
import logging
import ast

# Parent Directory imports
sys.path.append( "../utils" )
from mqtt_client import *
from density_clustering import *
from sql_utils import *

# Instantiate the logger
logging.basicConfig( format='%(levelname)s: %(message)s', level=logging.INFO )

# Define callback function for MQTT message callback
def on_message( client, userdata, message ):
    """Callback function for receiving messages."""
    msg = message.payload.decode( "utf-8" )
    store.msg_queue.append( msg )
    logging.info( "\n\tTopic: {}\n\tMessage: {}\n\tRetained: {}".format(
                  message.topic,msg, message.retain ) )

    if ( message.retain == 1 ):
        logging.info( "This was a retained message." )


# Set up argument parser
parser = argparse.ArgumentParser()
parser.add_argument( '--broker-ip', help='IP Address of the MQTT Broker. ' + \
                           'If no IP is specified, MQTT will not be used.',
                    required=True)
parser.add_argument('--client-name', help='Name of the MQTT Client.',
                    default='store1')
parser.add_argument('--subscribe', help='MQTT topic to subscrib to. ' + \
                                        'Default is test/occupancy.',
                    default='test/occupancy')
parser.add_argument('--camera-count', help='Number of total camera devices' + \
                              'communicating to the server for this detection',
                    default=2)
parser.add_argument('--group-suffix', help='Suffix Group for SQL Authentication.',
                    default='eecapstone')
parser.add_argument('--sql-table', help='Name of SQL Table to insert data into.',
                    default='occupancy')

# Parse arguments
args = parser.parse_args()
    
broker_ip = args.broker_ip
client_name = args.client_name
subscribe_topic = args.subscribe
num_cameras = int(args.camera_count)
suffix_group = args.group_suffix
table_name = args.sql_table

# Validate input arguments
if not num_cameras > 0:
    raise Exception("[-] Invalid number of camera devices. At least one " + \
                    "camera device is required.")

# Instantiate MQTT Client object, set the on_message callback, connect to broker
store = MQTTClient( broker_ip, client_name )
store.client.on_message = on_message
store.connect()

# Begin the thread for MQTT communication, subscribe to topic, publish UPDATE
store.loop_start()
store.subscribe( "test/occupancy")
# Publish to topic, QoS - quality of service: double checking, do not retain 
store.publish( "eecapstone/snapshot", "UPDATE", qos = 2, retain = False )

# Initiate flag for receiving data from all cameras
data_received = False

# Begin infinite loop until data from all cameras are received
while not data_received:
    # Check if the message queue has messages equal to number of cameras
        if len( store.msg_queue ) == num_cameras:
            # Grab the message from the queue
            incoming_data1 = store.msg_queue.pop()
            incoming_data2 = store.msg_queue.pop()
            # Data captured, break from the loop
            data_received = True

# Validate data are lists before appending
try:
    data1_list = ast.literal_eval( incoming_data1 )
    data2_list = ast.literal_eval( incoming_data2 )
except Exception as error:
    logging.error("[-] Error collecting input data from MQTT suscribe. " + \
                    "Data collected was not in list format.")
    print( error )
    exit(1)

# Display from log and combine all occupant locations into one list
print( "Incoming Data 1: ", data1_list )
print( "Incoming Data 2: ", data2_list )
all_locations = data1_list + data2_list

# Pass total locations list to clustering algorithm
total_occupants = Count_Clusters( all_locations )
print( "Total occupants detected: ", total_occupants )

# Insert data into SQL table
sql_values = ["current_timestamp()", 196, total_occupants]
insert_into_sql(suffix_group, table_name, sql_values)
print("SQL DATA: ", sql_values)

print("DONE")   
    
