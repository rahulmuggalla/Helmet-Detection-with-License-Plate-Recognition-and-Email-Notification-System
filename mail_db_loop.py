import cv2 # for computer vision.
import numpy as np # for scientific computing with Python
import pandas as pd # for data analysis
import requests
import json
import os
import smtplib # for sending emails
from email import encoders # for encoding email attachments
from email.mime.base import MIMEBase # for the implementation of MIME (Multipurpose Internet Mail Extensions)
from email.mime.multipart import MIMEMultipart # A class to represent a MIME Multipart message, as used in email
from email.mime.text import MIMEText # A class to represent plain text in email messages

def recognize_plate(image_path):
    # Set your API key and endpoint URL
    API_KEY = '2cde24fbebdb106dbb39dce0a6ec5132cb585074'
    API_URL = 'https://api.platerecognizer.com/v1/plate-reader/'

    # Read the image file as binary data
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # Make the API request
    response = requests.post(API_URL,
                             headers={'Authorization': f'Token {API_KEY}'},
                             files={'upload': image_data})

    try:
        # Parse the JSON response
        results = json.loads(response.text)

        # Extract license plate information if available
        if 'results' in results:
            plate_info = results['results'][0]
            plate = plate_info['plate']
            confidence = plate_info['score']
            #return f'License plate: {plate} (confidence {confidence})'
            return plate

        else:
            return 'No license plates found in image.'
    except:
        if response.status_code == 201:
            return 'Number Plate Text Not Recognized'
        else:
            # Handle any errors that occurred during the API request or response parsing
            return 'Error: Unknown Error'

def send_email(to_email, subject, body, attachment):

    from_email = "rahulmuggalla02@gmail.com" # Defining the sender email
    password = "gxnlvbfnssorjgkt" # Defining the sender password

    msg = MIMEMultipart() # Creating a MIME object
    msg['From'] = from_email # Adding the sender email to the message
    msg['To'] = to_email # Adding the recipient email to the message
    msg['Subject'] = subject # Adding the subject of the email to the message
    msg.attach(MIMEText(body, 'plain')) # Adding the body of the email to the message

    # Opening the attachment to be sent
    with open(attachment, "rb") as f:
        # Creating a MIME object for the attachment
        attach = MIMEBase('application', 'octet-stream', Name=attachment)

        # Setting the payload of the attachment
        attach.set_payload((f).read())

    encoders.encode_base64(attach) # Encoding the attachment

    # Adding headers to the attachment
    attach.add_header('Content-Decomposition', 'attachment', filename=attachment)
    msg.attach(attach) # Attaching the attachment to the message

    try:
        # Connecting to the Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)

        # Starting the encrypted connection
        server.starttls()
        # Login to the email account
        server.login(from_email, password)

        # Converting the message to a string
        text = msg.as_string()

        # Sending the email
        server.sendmail(from_email, to_email, text)
        # Quitting the SMTP server
        server.quit()

        # Printing a success message
        print("Email sent to " + to_email)
    except Exception as e:
        # Printing an error message if an error occurred while sending the email
        return(f"An error occurred while sending the email: {e}")
    return "netwoking issue"