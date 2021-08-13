- [smart-postbox](#smart-postbox)
  * [Main idea](#main-idea)
  * [Prototype](#prototype)
  * [Used components](#used-components)
  * [Setup on 1st Raspberry Pi](#setup-on-1st-raspberry-pi)
  * [Data Flow](#data-flow)
  * [Configure](#configure)
  * [How to use](#how-to-use)
 


# smart-postbox

## Main idea:
<img src="main_idea.png" width="50%" height="50%">

## Prototype
<img src="prototype.png" width="50%" height="50%">

## Used components:
<pre>
1. 2 Raspberry Pi 3 Model B
2. Picamera
3. PIR motion sensor
4. LED
</pre>

## Setup on 1st Raspberry Pi
<img src="postbox_setup_circual_diagram.png" width="30%" height="30%">
<img src="setup.png" width="30%" height="30%">
<img src="setup_upside_down.png" width="30%" height="30%">

# Data Flow
<img src="data_flow.jpg" width="30%" height="30%">


# Configure
1. first configure Google Vision API and get your key
2. then create a file named "credentials" containing sender_email, sender_password, receiver_email like below:
<pre>
sender@example.com
password1234
receiver@example.com
</pre>

# How to use
1. run [pir.py](pir.py) on the 1st Raspberry Pi <br />
2. run [camera_2.py](camera_2.py) using Flask run on the 1st Raspberry Pi <br />
3. Start Google Vision by exporting your key on the 2nd Raspberry Pi
4. run [ocr.py](ocr.py) using Flask run on the 2nd Raspberry Pi 

[pir.py](pir.py) detects new post insertion <br />
[camera_2.py](camera_2.py) takes picture and sends it to the 2nd Raspberry Pi <br />
[ocr.py](ocr.py) detects text on the post, applies filters and sends email<br /><br />

