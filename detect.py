import cv2
import pandas as pd
from ultralytics import YOLO
import os
import numpy as np # for scientific computing with Python
import pandas as pd # for data analysis
import requests
import json
import smtplib # for sending emails
from email import encoders # for encoding email attachments
from email.mime.base import MIMEBase # for the implementation of MIME (Multipurpose Internet Mail Extensions)
from email.mime.multipart import MIMEMultipart # A class to represent a MIME Multipart message, as used in email
from email.mime.text import MIMEText # A class to represent plain text in email messages

# Load the pre-trained YOLO model
model = YOLO('best.pt')

video = 'sample.mp4'

# Read the COCO class list from a file
with open("coco.txt", "r") as my_file:
    data = my_file.read()
class_list = data.split("\n")
print('Classes Names :', class_list)

# Create a folder for saving cropped images of "Person_Bike" objects
person_bike_folder = "Person_Bike"
if not os.path.exists(person_bike_folder):
    os.makedirs(person_bike_folder)

# Create a folder for saving cropped images of "No_Helmet" objects
no_helmet_folder = 'No_Helmet'
if not os.path.exists(no_helmet_folder):
    os.makedirs(no_helmet_folder)

def save_bike(video_path):

    # Mouse callback function for capturing RGB values of pixels
    def RGB(event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            colorsBGR = [x, y]
            print(colorsBGR)

    # Create a named window and set the mouse callback function
    cv2.namedWindow('RGB')
    cv2.setMouseCallback('RGB', RGB)

    # Open a video file for capturing frames
    cap = cv2.VideoCapture(video_path)

    count = 0

    # Loop through the video frames
    while True:
        ret, frame = cap.read()
        count += 1

        if not ret:
            break

        # Skip frames to process every third frame
        if count % 3 != 0:
            continue

        # Resize the frame to a fixed size
        frame = cv2.resize(frame, (1020, 500))

        # Perform object detection on the frame
        results = model.predict(frame)
        a = results[0].boxes.boxes
        px = pd.DataFrame(a).astype("float")

        # Loop through the detected objects
        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]
            print(c)

            # Draw bounding boxes and class labels on the frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)

            # Save cropped images of "Person_Bike" objects
            if "Person_Bike" in c:
                person_bike_img = frame[y1:y2, x1:x2]
                img_name = os.path.join(person_bike_folder, f"person_bike_{count}.jpg")
                cv2.imwrite(img_name, person_bike_img)

        # Display the frame with objects detected
        cv2.imshow("Person Bike", frame)

        # Break the loop if 'Esc' key is pressed
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Close all windows
    cv2.destroyAllWindows()

def save_no_helmet(image_folder, no_helmet_folder=no_helmet_folder):

    # Loop through every image in the image folder
    for image_file in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_file)
        frame = cv2.imread(image_path)  # Read image using OpenCV
        results = model.predict(frame)  # Predict using the YOLO model
        a = results[0].boxes.boxes
        px = pd.DataFrame(a).astype("float")  # Convert predictions to a Pandas DataFrame
        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]  # Get the class label based on the predicted class index

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw bounding box on the image
            cv2.putText(frame, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)  # Add text label on the image

            if 'No_Helmet' in c:
                # Save the image without helmet to the "no-helmet" folder
                cv2.imwrite(os.path.join(no_helmet_folder, image_file), frame)
                break  # Break out of the loop after detecting one "No_Helmet" class
        cv2.imshow("Save No Helmet", frame)  # Show the image with bounding boxes and labels

        # Break the loop if 'Esc' key is pressed
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()

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
        # Handle any errors that occurred during the API request or response parsing
        return f'Error: API request failed with status code {response.status_code}\nMessage: {response.text}'

def send_email(to_email, subject, body, attachment):

    from_email = "email" # Defining the sender email
    password = "password" # Defining the sender password

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
        print(f"An error occurred while sending the email: {e}")

if __name__ == "__main__":

    save_bike(video)

    save_no_helmet(person_bike_folder)

    # Load the CSV file containing user data
    user_data = pd.read_csv("user_data.csv")

    # Set to keep track of recognized license plates
    recognized_plates = set()

    # Loop through all images in the folder
    for filename in os.listdir(no_helmet_folder):
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
            # Construct the full image path
            image_path = os.path.join(no_helmet_folder, filename)

            # Recognize the license plate from the image
            license_plate = recognize_plate(image_path)

            # Check if the recognized license plate has already been identified
            if license_plate in recognized_plates:
                # Print a message and skip to the next image
                print(f"License Plate already identified earlier : {license_plate}")
                continue
            else:
                # Add the recognized license plate to the set
                recognized_plates.add(license_plate)

            # Check if the recognized license plate is in the user data
            if license_plate in user_data['License Plate'].values:
                # Get the user details from the user data
                user_details = user_data[user_data['License Plate'] == license_plate]

                # Print the user data
                print(user_details)

                # Extract the violation details
                name = user_details['Name'].values[0]
                email = user_details['Email'].values[0]

                # Compose the email subject and body
                subject = f'Violation Alert: No Helmet'
                body = f'Dear {name},\n\nThis is to inform you that a violation has been detected in your vehicle with license plate number {license_plate}. The violation is related to not wearing a helmet while driving.\n\nPlease ensure compliance with traffic rules and regulations in the future.\n\nSincerely,\nTraffic Violation Monitoring System'

                # Send the email with the image attachment
                send_email(email, subject, body, image_path)
            else:
                print(f'No user data found for license plate: {license_plate}')
        else:
            print(f'Invalid file format for file: {filename}')