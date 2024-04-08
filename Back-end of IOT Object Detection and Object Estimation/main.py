import datetime

import cv2 as cv
import tkinter as tk
import threading
import pygame
from PIL import Image, ImageTk

# Adding Data to Firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(r"chandu_key.json")
firebase_admin.initialize_app(cred)
firebase_database = firestore.client()


# Distance constants
KNOWN_DISTANCE = 45  # INCHES
PERSON_WIDTH = 16  # INCHES
MOBILE_WIDTH = 3.0  # INCHES
VEHICLE_WIDTH = 60.0  # INCHES (Assuming a standard car width)

# Object detector constants
CONFIDENCE_THRESHOLD = 0.4
NMS_THRESHOLD = 0.3

# Colors for object detected
COLORS = [(255, 0, 0), (255, 0, 255), (0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Defining fonts
FONTS = cv.FONT_HERSHEY_COMPLEX

# Getting class names from classes.txt file
class_names = []
with open("classes.txt", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

# Setting up OpenCV net
yoloNet = cv.dnn.readNet('yolov4-tiny.weights', 'yolov4-tiny.cfg')

yoloNet.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
yoloNet.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA_FP16)

model = cv.dnn_DetectionModel(yoloNet)
model.setInputParams(size=(416, 416), scale=1 / 255, swapRB=True)

# Load the alert sound
pygame.mixer.init()
alert_sound = pygame.mixer.Sound('alert_sound.mp3')

# Threshold distance for triggering the alert (in inches)
threshold_distance = 25  # Adjust as needed

# Flag to track whether the alert has been played or not
alert_played = False

# Object states dictionary to track the distance of each object
object_states = {}


# Object detector function/method
def object_detector(image):
    classes, scores, boxes = model.detect(image, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
    # Creating an empty list to add object's data
    data_list = []
    for (classid, score, box) in zip(classes, scores, boxes):
        # Define color of each object based on its class id
        color = COLORS[int(classid) % len(COLORS)]
        label = "%s : %f" % (class_names[classid], score)

        # Draw rectangle and label on the object
        cv.rectangle(image, box, color, 2)
        cv.putText(image, label, (box[0], box[1] - 14), FONTS, 0.5, color, 2)

        # Getting the data
        # 1: class name, 2: object width in pixels, 3: position where text has to be drawn (distance)
        data_list.append([class_names[classid], box[2], (box[0], box[1] - 2)])

    # Return list containing the object data
    return data_list


def focal_length_finder(measured_distance, real_width, width_in_rf):
    focal_length = (width_in_rf * measured_distance) / real_width
    return focal_length


def distance_finder(focal_length, real_object_width, width_in_frame):
    distance = (real_object_width * focal_length) / width_in_frame
    return distance


def play_alert():
    global alert_played
    if not alert_played:
        alert_sound.play()
        alert_played = True


def stop_alert():
    global alert_played
    if alert_played:
        alert_sound.stop()
        alert_played = False


# Distance constants, object detector constants, colors, fonts, class names, YOLO model setup, and alert settings...

def process_video():
    global alert_played
    global object_states

    # Reading the reference images from directory and initializing the camera
    ref_person = cv.imread('ReferenceImages/image14.png')
    ref_mobile = cv.imread('ReferenceImages/image4.png')

    mobile_data = object_detector(ref_mobile)
    mobile_width_in_rf = mobile_data[1][1]

    person_data = object_detector(ref_person)
    person_width_in_rf = person_data[0][1]

    focal_person = focal_length_finder(KNOWN_DISTANCE, PERSON_WIDTH, person_width_in_rf)
    focal_mobile = focal_length_finder(KNOWN_DISTANCE, MOBILE_WIDTH, mobile_width_in_rf)

    cap = cv.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        data = object_detector(frame)
        objects_within_threshold = False
        for d in data:
            if d[0] in ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
                        'traffic light', 'fire hydrant', 'stop sign', 'parking meter']:
                if d[0] == 'person':
                    distance = distance_finder(focal_person, PERSON_WIDTH, d[1])
                elif d[0] == 'car':
                    distance = distance_finder(focal_person, VEHICLE_WIDTH, d[1])
                else:
                    distance = distance_finder(focal_mobile, MOBILE_WIDTH, d[1])

                x, y = d[2]

                cv.rectangle(frame, (x, y - 3), (x + 150, y + 23), BLACK, -1)
                cv.putText(frame, f'Dis: {round(distance, 2)} inch', (x + 5, y + 13), FONTS, 0.48, GREEN, 2)

                # Get current timestamp
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if distance < threshold_distance:
                    obj_name = d[0]
                    obj_distance = distance
                    obj_data = {
                        'timestamp': current_time,
                        'name': obj_name,
                        'distance': obj_distance
                    }

                    # Adding a new Document to the Existing Collection
                    firebase_reference = firebase_database.collection('Object Detection and Distance Estimation').document()
                    firebase_reference.set(obj_data)
                    print(obj_data)

                    objects_within_threshold = True

                object_states[d[0]] = distance

        if objects_within_threshold:
            play_alert()
        else:
            stop_alert()

        frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_tk = ImageTk.PhotoImage(image=frame_pil)

        label.config(image=frame_tk)
        label.image = frame_tk

        root.update()

        key = cv.waitKey(1)
        if key == ord('q'):
            break

    # Release the camera capture and destroy all OpenCV windows
    cap.release()
    cv.destroyAllWindows()

def start_processing():
    threading.Thread(target=process_video).start()

def close_program():
    # Release the camera capture and destroy all OpenCV windows
    cv.destroyAllWindows()
    root.destroy()

# Create Tkinter window
root = tk.Tk()
root.title("Vehicle Detection App")

# Add project details label
project_label = tk.Label(root, text="Vehicle Detection System\n(Using YOLOv4 and Thermal Camera)",
                         font=('Arial', 20, 'bold'))
project_label.pack(pady=20)

# Create label for displaying video stream
label = tk.Label(root)
label.pack()

# Create a frame for buttons
button_frame = tk.Frame(root)
button_frame.pack()

# Start processing button
start_button = tk.Button(button_frame, text="Start Processing", command=start_processing)
start_button.grid(row=0, column=0, padx=10)

# Close program button
close_button = tk.Button(button_frame, text="Close Program", command=close_program)
close_button.grid(row=0, column=1, padx=10)

# Run the Tkinter event loop
root.mainloop()