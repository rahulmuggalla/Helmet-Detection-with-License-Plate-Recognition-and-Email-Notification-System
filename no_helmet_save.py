import cv2
import pandas as pd
import os
from ultralytics import YOLO


def save_no_helmet(image_folder):

    # Create the "no-helmet" folder if it doesn't exist
    if not os.path.exists(no_helmet_folder):
        os.makedirs(no_helmet_folder)
    
    # Loop through every image in the image folder
    for image_file in os.listdir(image_folder):
        a = results[0].boxes.boxes
        px = pd.DataFrame(a).astype("float")  # Convert predictions to a Pandas DataFrame
        for index, row in px.iterrows():
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]  # Get the class label based on the predicted class index

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw bounding box on the image
            cv2.putText(frame, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)  # Add text label on the image

            if 'No_Helmet' in c:
                # Save the image without helmet to the "no-helmet" folder
                cv2.imwrite(os.path.join(no_helmet_folder, image_file), frame)
