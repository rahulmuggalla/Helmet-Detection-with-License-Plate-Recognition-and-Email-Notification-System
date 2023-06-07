import cv2
import pandas as pd
import os
from ultralytics import YOLO


def save_no_helmet_img(image_folder):

    # Create the "no-helmet" folder if it doesn't exist
    if not os.path.exists(no_helmet_folder):
        os.makedirs(no_helmet_folder)
    
    # Loop through every image in the image folder
    for image_file in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_file)
        frame = cv2.imread(image_path)  # Read image using OpenCV
        results = model.predict(frame)  # Predict using the YOLO model
        a = results[0].boxes.boxes
        px = pd.DataFrame(a).astype("float")  # Convert predictions to a Pandas DataFrame
        for index, row in px.iterrows():
            y2 = int(row[3])
            d = int(row[5])

            if 'No_Helmet' in c:
                # Save the image without helmet to the "no-helmet" folder
                cv2.imwrite(os.path.join(no_helmet_folder, image_file), frame)
