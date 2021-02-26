#Add MQTT publish UPDATE command
#publish "UPDATE" to MQTT topic "eecapstone/snapshot"
#Add MQTT subscribe loop to collet data from all cameras
#Check message list length against number of cameras
#if message length == number  of cameras, break

 
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
    
    
    #this is where we compare the camera count to the message list count, do we want to enable log through mosquitto to see who is subscribed? 
    
    
    
