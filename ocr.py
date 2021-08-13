#!/usr/bin/env python3

from flask import Flask, request
from google.cloud import vision
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path
import re
import requests

client = vision.ImageAnnotatorClient()

app = Flask(__name__)

IMAGE_PATH = "/home/pi/Desktop/"
IMAGE_NAME = "image.jpeg"
ATTACHED_IMAGE = IMAGE_PATH + IMAGE_NAME

with open("credentials", "r") as credentials:
    content = credentials.readlines()
    SENDER, PASSWORD, RECEIVER = [x.rstrip() for x in content]

MINIMUM_CHARACTER_COUNT = 20
MAXIMUM_OCR_RETRY = 3

SENDER_BLACKLIST = ["kibek"]
RECEIVER_WHITELIST = ["fikrat", "bayram", "bilal"]


def add_image_to_attachment(msg, attachment_location):
    if attachment_location is None:
        return

    filename = os.path.basename(attachment_location)
    part = MIMEBase("application", "octet-stream")
    with open(attachment_location, "rb") as attachment:
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={filename}")
    msg.attach(part)


def add_sender_receiver_info(msg, email_recipient, email_subject):
    msg["From"] = SENDER
    msg["To"] = email_recipient
    msg["Subject"] = email_subject


def extract_text_from_image(content):
    # extract text on the image
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    return response.text_annotations[0].description


def trim_string(s):
    return re.sub("[\s+]", "", s)


def correct_text(email_body):
    # correct Herrn
    if "Herm" in email_body:
        email_body = email_body.replace("Herm", "Herrn")
    if "Hem" in email_body:
        email_body = email_body.replace("Hem", "Herrn")
    if "Herrn" in email_body:
        email_body = email_body.replace("Herrn", "\nHerrn")
    return email_body


def is_sender_in_blacklist(email_body):
    for sender in SENDER_BLACKLIST:
        if sender in email_body.lower():
            return True
    return False


def is_receiver_in_whitelist(email_body):
    for receiver in RECEIVER_WHITELIST:
        if receiver in email_body.lower():
            return True
    return False


def send_email(email_recipient, email_subject, email_message, attachment_location=None):
    msg = MIMEMultipart()

    add_sender_receiver_info(msg, email_recipient, email_subject)

    msg.attach(MIMEText(email_message, "plain"))

    add_image_to_attachment(msg, attachment_location)

    try:
        server = smtplib.SMTP("smtp.office365.com", 587)
        server.ehlo()
        server.starttls()
        server.login(SENDER, PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER, email_recipient, text)
        print("email sent to " + email_recipient)
        return True
    except Exception:
        print("SMTP server connection error")
        return False
    finally:
        server.quit()


@app.route("/send-picture", methods=["POST"])
def sendPicture():
    # Get image
    image_file = request.files["image"]
    content = image_file.read()

    # save image
    with open(IMAGE_NAME, "wb") as file:
        file.write(content)

    email_body = extract_text_from_image(content)

    count = 0

    email_subject = ""

    while (
        len(trim_string(email_body)) < MINIMUM_CHARACTER_COUNT
        and count < MAXIMUM_OCR_RETRY
    ):
        print("retake picture...")
        r = requests.get("http://192.168.0.150:5000/get-picture")
        content = r.content

        # save image
        with open(IMAGE_NAME, "wb") as file:
            file.write(content)

        email_body = extract_text_from_image(content)

        count += 1

    email_body = correct_text(email_body)

    # send email if it is for me and is not from kibek (spam)
    if not is_receiver_in_whitelist(email_body) or is_sender_in_blacklist(email_body):
        return "200"

    if count == MAXIMUM_OCR_RETRY:
        email_subject = "You got a new post, but no text on it"
    else:
        email_subject = "You got a new post"
    send_email(
        RECEIVER,
        email_subject,
        email_body,
        ATTACHED_IMAGE,
    )

    return "200"  # "", 200, {}
