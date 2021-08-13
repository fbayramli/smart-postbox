#!/usr/bin/env python3

from flask import Flask, send_file
from PIL import Image
import RPi.GPIO as GPIO
from time import sleep
from picamera import PiCamera
from queue import Queue
from threading import Thread
import requests
from time import time
from io import BytesIO

LED_PIN = 16  # Broadcom pin 23 (P1 pin 16)

queue = Queue()
camera = None
app = Flask(__name__)


def setup_pi():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_PIN, GPIO.OUT)  # LED pin set as output
    GPIO.output(LED_PIN, GPIO.LOW)


def setup_camera():
    camera = PiCamera()
    camera.resolution = (3280, 2464)
    camera.sharpness = 100
    camera.awb_mode = "auto"
    camera.image_effect = "colorbalance"
    camera.image_effect_params = (256.0, 256.0, 256.0)
    camera.saturation = -100
    return camera


def send_image(queue):
    while queue.get():
        with capture() as stream:
            requests.post(
                "http://192.168.0.151:5000/send-picture",
                files={"image": stream, "mimetype": "image/jpeg"},
            )


def capture():
    with BytesIO() as read_stream:
        GPIO.output(LED_PIN, GPIO.HIGH)
        sleep(2)
        camera.capture(read_stream, "jpeg")
        GPIO.output(LED_PIN, GPIO.LOW)
        read_stream.seek(0)
        image = Image.open(read_stream).rotate(90)

    write_stream = BytesIO()
    image.save(write_stream, "JPEG")
    write_stream.seek(0)
    return write_stream


@app.route("/get-picture", methods=["GET"])
def getPicture():
    with capture() as stream:
        return send_file(stream, mimetype="image/jpeg")


@app.route("/pir", methods=["GET"])
def pir_signal_handler():
    queue.put(time())
    return "200"


if __name__ == "__main__":
    try:
        setup_pi()
        camera = setup_camera()
        Thread(target=send_image, args=((queue),), daemon=True).start()
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        camera.close()
        GPIO.cleanup()
