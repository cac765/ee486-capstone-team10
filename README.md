# ee486-capstone-team10
This is the primary repository for the EE486 Team 10 Capstone project, which is an IoT People Counting solution as an embedded device.

# TensorFlow Lite on the Raspberry Pi

*Resource*

* [TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/Raspberry_Pi_Guide.md at master · EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi · GitHub](https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Raspberry_Pi_Guide.md) → The following tutorial is based on EdjeElectronics' guide here.

* [Python quickstart: TensorFlow Lite](https://www.tensorflow.org/lite/guide/python) → TensorFlow Lite documentation.



This document will contain notes and code required to begin running TensorFlow Lite on a Raspberry Pi 3.



## Update Your Pi /  Enable Camera

First, it is a good idea to make sure your Pi is up to date with its software. Run the commands below to fully update your system. This may take a while, depending on how long it’s been since your Pi was last updated.

```shell
sudo apt-get update -y && sudo apt-get upgrade -y && sudo apt-get dist-upgrade -y
```

Once the upgrade is complete, we can make sure the camera port is enabled. Run the command below to open the config menu.

```shell
sudo raspi-config
```

Once in the menu, navigate to `interface options` → `camera`. Select `yes` to enable the camera interface. The Pi will ask to reboot.



## Clone this Repository

Clone the repositories used for testing TensorFlow Lite models. Get to a nice root directory of your choice *(personally, I always make a **repos** folder where all of my repositories can live)*, then run the commands below.

```shell
git clone https://github.com/cac765/iot-people-counter.git
cd iot-people-counter/tflite1
```



## Setup Virtual Environments

First, we will create a virtual environment to handle all of our packages in order to avoid verison conflicts with the system. Begin by installing Python's virtualenv and the virtualenvwrapper.

```shell
pip3 install virtualenv virtualenvwrapper
```

> **<mark>Warning:</mark>** The script virtualenv is installed in '/home/pi/.local/bin' which is not on PATH.  
> Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.

Don't worry if you recieve this warning, we will fix it in the next step here. We will now configure out `.bashrc` file with the proper environment variables. Edit the `.bashrc` file by running the following command:

```shell
sudo nano ~/.bashrc
```

Then, add the following lines to the end of the file:

```bash
export PATH=$PATH:/home/pi/.local/bin/
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
source /home/pi/.local/bin/virtualenvwrapper.sh
```

Save and exit the file. Rerun the file with the following command:

```shell
source ~/.bashrc
```

> If you get something like the following error:
> 
> `-bash: /usr/local/bin/virtualenvwrapper.sh: No such file or directory`
> 
> This is because the virtualenvwrapper did not download in the specified location, or has an incorrect filepath. You will have to find where the **virtualenvwrapper.sh** script is located, and change the path in the `.bashrc` file to the correct path.
> 
> *Keep in mind that the commands above assume the **username** on the system is* `pi`. 
> 
> *If this is not the case for your system, be sure to update those filepaths accordingly.*



Now we are ready to create a virtual environment to handle all of our packages. To create a virtual environment named `tflite1`, run the command below:

```shell
mkvirtualenv tflite1 -p /usr/bin/python3
```



### Activating/Deactivating Virtual Environments

To activate your virtual environment → `workon tflite1`

To deactivate → `deactivate`



## Install Dependencies

Now we are ready to install of the dependencies required to run object detection on the Raspberry Pi. First, **make sure that your virtual environment is activated** with the command `workon tflite1`.

EdjeElectronics has made things extremely easy for us and has already placed all of the requirements needed in a shell script, so simply run the script with the command below from the `tflite1` directory.

```shell
bash get_pi_requirements.sh
```



### A Note on the Dependencies

In order to run a TensorFlow-Lite model on the Raspberry Pi, we do not need the full TensorFlow library. The full library is bulky and designed for loading models, training models, saving models, etc. For our case, we simply need the modules from TensorFlow that are able to **interpret** our pre-trained model. Therefore, we will only need to install the **TensorFlow-Lite Interpreter**.



## Setup TensorFlow-Lite Detection Model

Now we are ready to grab the pre-trained detection model already converted to TensorFlow Lite and ready to go. Get the model and unzip it by running the commands below. Here, we will be storing our model in the **Sample_TFLite_model** directory.

```shell
wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
unzip coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip -d Sample_TFLite_model
```



## Test the Model

Now let’s test the model! To run the model on a live PiCamera, run the command below.

* **NOTE: be sure that you have some sort of GUI support with your current Pi session, i.e., a physical monitor or remote desktop. SSH will NOT work!!**

```shell
python3 TFLite_detection_webcam.py --modeldir=Sample_TFLite_model
```

> **NOTE:** Your camera view may be flipped upside down. To resolve this, we simply have to add one line to the code file that flips the camera view. Follow the steps below to resolve this.
> 
> 1. **Exit Virtual Environment:** `deactivate`
> 
> 2. **Download nedit:** `sudo apt-get install nedit`
> 
> 3. **Open file with nedit:** `nedit TFLite_detection_webcam.py`
> 
> 4. **Show Line Numbers:** Click **“Preferences”** → **“Show Line Numbers”**
> 
> 5. **AT LINE 179:** Check out the following code: 
>    
>    ```python
>    frame = cv2.flip( frame, -1 ) ### ADDED HERE TO FLIP IMAGE FROM VIDEO STREAM - COREY CLINE
>    ```
>    
>    * If your video is flipped, comment this code out. If the frame is flipped on a different orientation, refer to the documentation provided on **step 7.**
> 
> 6. **Save the File:** `Ctrl + S` and Exit.
> 
> 7. **Test the Script Again:** Check to see if the video is properly flipped. If the image seems to be backwards **horizontally** now, try changing the **-1** to **0**. Refer [here](https://www.geeksforgeeks.org/python-opencv-cv2-flip-method/ "https://www.geeksforgeeks.org/python-opencv-cv2-flip-method/") for documentation on cv2.flip().



## Save Recordings (Optional)

To save the output when running the model, add the `--record` flag. Here's the command for example:

```shell
python3 TFLite_detection_webcam.py --modeldir=Sample_TFLite_model --record
```

This will record the session at the framerate specified in the VideoWriter object initialization. Refer to line 166:

```python
writer = cv2.VideoWriter( "output/output.avi", cv2.VideoWriter_fourcc( *"MJPG" ), 4, (imW,imH) ) ### ADDED HERE TO SAVE VIDEO AS FILE - COREY CLINE
```

> **NOTE:** The parameter **4** in the line above represents the frame rate. For a Pi 3, the video runs at about **2** fps. If you are running at a different frame rate when you test the video, change this number so that the saved video is not significantly slowed down or sped up. (For a Pi 4, the frame rate is about **4** fps).
> 
> *In summary, you want to do your best to match the video stream framerate to the VideoWriter framerate. This will provide an accurate recording of the model's performance.*

Now we can run the file and check to make sure it was saved correctly in the output folder. Another note on this, the file may not be playable from the Raspberry Pi VLC Media Player, but it can be transferred to your local machine via sftp. For more information about SFTP protocol, refer to [this link](https://cat.pdx.edu/platforms/linux/remote-access/using-sftp-for-remote-file-transfer-from-command-line/ "https://cat.pdx.edu/platforms/linux/remote-access/using-sftp-for-remote-file-transfer-from-command-line/").

> Keep in mind that the script will overwrite the file named `output.avi` located in the `output` directory. If you'd like to avoid this, be sure to either SFTP the file to your local machine, or move it to a different directory within the Pi.



## Run Edge TPU Object Detection Models Using the Coral USB Accelerator

This documentation is adapted from the EdjeElectronics tutorial linked [here.](https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Raspberry_Pi_Guide.md "https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Raspberry_Pi_Guide.md") This section follows “Section 2 - Run Edge TPU Object Detection Models on the Raspberry Pi Using the Coral USB Accelerator”.

---

The USB Accelerator uses the Edge TPU (tensor processing unit), which is an ASIC (application-specific integrated circuit) chip specially designed with highly parallelized ALUs (arithmetic logic units). While GPUs (graphics processing units) also have many parallelized ALUs, **the TPU has one key difference: the ALUs are directly connected to each other**.

The output of one ALU can be directly passed to the input of the next ALU without having to be stored and retrieved from the memory buffer. The extreme parallelization and removal of the memory bottleneck mean the TPU can perform up to **4 trillion arithmetic operations per second**! This is perfect for running deep neural networks, which require millions of multiply-accumulate operations to generate outputs from a single batch of input data.



*Resource*

* Here’s an image of the [hardware](https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/doc/Coral_and_EdgeTPU2.png "https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/doc/Coral_and_EdgeTPU2.png").

* If you're a computer architecture nerd like me and want to learn more about the **Edge TPU**, [here’s a great article that explains how it works.](https://cloud.google.com/blog/products/ai-machine-learning/what-makes-tpus-fine-tuned-for-deep-learning "https://cloud.google.com/blog/products/ai-machine-learning/what-makes-tpus-fine-tuned-for-deep-learning")



### Install libedgetpu library

First, we’ll download and install the Edge TPU runtime, which is the library needed to interface with the USB Accelerator. These instructions follow the [USB Accelerator setup guide from the official Coral website](https://coral.ai/docs/accelerator/get-started/ "https://coral.ai/docs/accelerator/get-started/").

Open a command terminal and move into the `~/repos/iot-people-counter/tflite1` directory and activate the tflite1 virtual environment by issuing:

```shell
cd ~/repos/iot-people-counter/tflite1
workon tflite1
```

Add the Coral package repository to your apt-get distribution list by issuing the following commands:

```shell
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
```

Install the libedgetpu library by issuing:

```shell
sudo apt-get install libedgetpu1-std
```

Now that the libedgetpu runtime is installed, it’s time to set up an Edge TPU detection model to use it with.



### Set up Edge TPU detection model

Edge TPU models are TensorFlow Lite models that have been compiled specifically to run on Edge TPU devices like the Coral USB Accelerator. They reside in a .tflite file and are used the same way as a regular TFLite mode. We will keep the Edge TPU file in the same model folder as the TFLite model it was compiled from, and name it “edgetpu.tflite”.

> We will roll with using Google’s sample EdgeTPU model, but you can use your own custom EdgeTPU model if you trained a custom TFLite detection model.
> 
> Refer to “Option 2. Using your own custom Edge TPU model” and “Section 3 - Compile Custom Edge TPU Object Detection Models” in [this EdjeElectronics tutorial](https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Raspberry_Pi_Guide.md "https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Raspberry_Pi_Guide.md").

Google provides a sample EdgeTPU model that is compiled from the quantized SSDLite-MobileNet-v2. Download it and move it into the Sample_TFLite_model folder (while simultaneously renaming it to “edgetpu.tflite”) by issuing the following commands:

```shell
wget https://dl.google.com/coral/canned_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite
mv mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite Sample_TFLite_model/edgetpu.tflite
```

Now the sample Edge TPU model is all ready to go. It will use the same labelmap.txt file as the TFLite model, which should already be located in the Sample_TFLite_model folder.



### Run detection with Edge TPU

Now that everything is set up, it’s time to test out the Coral USB Accelerator! Make sure you free up memory and processing power by closing any programs you aren’t using. Make sure you have a webcam plugged in. Plug your Coral USB Accelerator into one of the USB ports of the Raspberry Pi.

* **NOTE:** If you’re using a Pi 4, make sure to plug it into one of the blue USB 3.0 ports.

Next, we need to add the main user to the **plugdev** group in order to access the Coral USB Accelerator, then reboot the Pi. Execute the following commands:

```shell
sudo usermod -aG plugdev [username]
sudo reboot
```

* **Replace [username] with the main user. The default username on a Raspberry Pi is “pi”.**

Now that we have done that, return to `~/repos/iot-people-counter/tflite1` and make sure the `tflite1` environment is activated by verifying that `(tflite1)` appears in front of the command prompt in your terminal.

Then run the `TFLite_detection_webcam.py` script with the `--edgetpu` argument:

```shell
python3 TFLite_detection_webcam.py --modeldir=Sample_TFLite_model --edgetpu
```

The `--edgetpu` argument tells the script to use the Coral USB Accelerator and the EdgeTPU-compiled .tflite file.

If you'd like to run the video or image detection scripts with the Accelerator, use these commands:

```shell
python3 TFLite_detection_video.py --modeldir=Sample_TFLite_model --edgetpu
python3 TFLite_detection_image.py --modeldir=Sample_TFLite_model --edgetpu
```

**Have fun with the Coral USB Accelerator!**



## Performance Analysis

| Pi 3 Solo                       | Pi 4 Solo                       | Pi 3 + Coral Accelerator        | Pi 4 + Coral Accelerator        |
| ------------------------------- | ------------------------------- | ------------------------------- | ------------------------------- |
| 2.0 FPS Live Feed → No Save     | 4.4 FPS Live Feed → No Save     | 9.5 FPS Live Feed → No Save     | 21.0 FPS Live Feed → No Save    |
| 1.4 FPS Live Feed → VideoWriter | 3.2 FPS Live Feed → VideoWriter | 3.0 FPS Live Feed → VideoWriter | 7.8 FPS Live Feed → VideoWriter |



