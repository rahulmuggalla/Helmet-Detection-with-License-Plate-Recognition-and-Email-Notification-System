import cv2
import pandas as pd
import os
from ultralytics import YOLO


def save_no_helmet_img(image_folder):

    model = YOLO('best.pt')  # Load YOLO model with 'best.pt' weights
    class_list = ['Helmet', 'No_Helmet', 'Number_Plate', 'Person_Bike']  # List of classes
    image_folder = 'static/img'  # Folder containing the person-bike images
    no_helmet_folder = 'static/No_Helmet_Img'  # Folder to save the images without helmets

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

    cv2.destroyAllWindows() # Close all windows
