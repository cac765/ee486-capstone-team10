import paho.mqtt.client as mqtt
import logging, time



def on_connect( client, userdata, flag, rc ):
    """
      Callback function when connection to the broker is established.
    """
    if ( rc == 0 ):
        client.connected_flag = True
        logging.info( "Connected to Broker! Returned code: %s\n" %rc )
    else:
        logging.info( "Failed to connect. Returned code: %s\n" %rc )



def on_disconnect( client, userdata, rc ):
    """
      Callback function when client has been disconnected from broker.
    """
    logging.info( "Disconnected from Broker. Returned code: %s\n" %rc )
    client.connected_flag = False
    client.disconnect_flag = True



def on_message( client, userdata, message ):
    """
      Callback function for receiving messages.
    """
    msg = str( message.payload )
    logging.info( "\tTopic: {}\n\tMessage: {}\n\tRetained: {}".format(
                  message.topic,msg, message.retain ) )

    if ( message.retain == 1 ):
        logging.info( "This was a retained message." )



def on_publish( client, userdata, mid ):
    """
      Callback function when topic is published.
    """
    logging.info( "Data published successfully." )



def on_subscribe( client, userdata, mid, granted_qos ):
    """
      Callback function when topic is subscribed.
    """
    logging.info( "Topic successfully subcribed with QoS: %s" %granted_qos )



def on_log( client, userdata, level, buf ):
    """
      Callback function for mqtt logger.
    """
    print( "MQTTClient log: ", buf )



class MQTTClient:

    def __init__( self, broker_ip, client_name ):
        """
          Class constructor.
        """
        self.broker_ip = broker_ip
        self.client_name = client_name

        self.client = mqtt.Client( client_name )

        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message
        self.client.on_publish = on_publish
        self.client.on_subscribe = on_subscribe
        self.client.on_log = on_log


    def connect( self, port = 1883 ):
        """
          Connect to broker IP at port.
        """
        logging.info( "Connecting to broker {}:{}".format( self.broker_ip, port ) )

        try:
            self.client.connect( self.broker_ip, port = port )
            time.sleep(2) # Wait to connect

        except Exception as error:
            print( error )


    def subscribe( self, topic ):
        """
          Subscribe to a topic.
        """
        logging.info( "Subscribing to topic %s" %topic )
        try:
            self.client.subscribe( topic )
        except Exception as error:
            print( error )


    def publish( self, topic, data, qos = 1, retain = False ):
        """
          Publish to a topic.
        """
        logging.info( "Publishing to topic %s" %topic )
        self.client.publish( topic, data, qos = qos, retain = retain )



