import cv2
import pandas as pd
from ultralytics import YOLO
import os

def save_bike(video_path):


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
            d = int(row[5])
            c = class_list[d]
            print(c)

            # Draw bounding boxes and class labels on the frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)


        # Display the frame with objects detected
        cv2.imshow("Person Bike", frame)
