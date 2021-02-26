#Add MQTT publish UPDATE command
#publish "UPDATE" to MQTT topic "eecapstone/snapshot"
#Add MQTT subscribe loop to collet data from all cameras
#Check message list length against number of cameras
#if message length == number  of cameras, break

# Standard library imports
import sys
import argparse

# Parent Directory imports
sys.path.append( "../utils" )
from mqtt_client import *


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
parser.add_argument( '--broker-ip', help='IP Address of the MQTT Broker. \
                            If no IP is specified, MQTT will not be used.',
                    required=True)
parser.add_argument('--client-name', help='Name of the MQTT Client.',
                    required=True)
parser.add_argument('--subscribe', help='MQTT topic to subscrib to. \
                                         Default is test/occupancy.',
                    default='test/occupancy')

# Parse arguments
args = parser.parse_args()
    
broker_ip = args.broker_ip
client_name = args.client_name
subscribe_topic = args.subscribe

# Validate input arguments??
    
store = MQTTClient( broker_ip, client_name )
#sets to run callback function
store.client.on_message = on_message
#connecting to broker
store.connect()
#starts a thread for MQTT messages
store.loop_start()
#subscribe to topic, qos-quality of service: double checking, retain- forget about it 
store.publish( "eecapstone/snapshot", "UPDATE", qos = 2, retain = False )
#subscribe and collect data from all cameras
store.subscribe( "test/occupancy")

data_received = False

while not data_received:
    # Check if the message queue has messages
        if len( store.msg_queue ) > 1:
            # Grab the message from the queue
            incoming_data1 = store.msg_queue.pop()
            incoming_data2 = store.msg_queue.pop()

            data_received = True

print( "Data 1: ", incoming_data1, "\nData 2: ", incoming_data2 )
print("DONE")
        
#if __name__ == "__main__":
#    main()
    
    
    
