import cv2
import pandas as pd
from ultralytics import YOLO
import os

def save_bike(video_path):

    # Load the pre-trained YOLO model
    model = YOLO('best.pt')

    # Read the COCO class list from a file
    with open("coco.txt", "r") as my_file:
        data = my_file.read()
    class_list = data.split("\n")
    print('Classes Names :', class_list)

    # Create a folder for saving cropped images of "Person_Bike" objects
    person_bike_folder = "static/Person_Bike"
    if not os.path.exists(person_bike_folder):
        os.makedirs(person_bike_folder)

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