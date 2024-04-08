# app.py
from flask import Flask, render_template, request, jsonify
import cv2 as cv
import numpy as np
import base64

app = Flask(__name__)

# Distance constants
KNOWN_DISTANCE = 45  # INCHES
PERSON_WIDTH = 16  # INCHES
MOBILE_WIDTH = 3.0  # INCHES
VEHICLE_WIDTH = 60.0  # INCHES (Assuming a standard car width)

# Object detector constant
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


# Reading the reference images from directory
ref_person = cv.imread('ReferenceImages/image14.png')
ref_mobile = cv.imread('ReferenceImages/image4.png')

mobile_data = object_detector(ref_mobile)
mobile_width_in_rf = mobile_data[1][1]

person_data = object_detector(ref_person)
person_width_in_rf = person_data[0][1]

print(f"Person width in pixels: {person_width_in_rf}, Mobile width in pixels: {mobile_width_in_rf}")

# Finding focal length
focal_person = focal_length_finder(KNOWN_DISTANCE, PERSON_WIDTH, person_width_in_rf)
focal_mobile = focal_length_finder(KNOWN_DISTANCE, MOBILE_WIDTH, mobile_width_in_rf)


# Route for index page
@app.route('/')
def index():
    return render_template('index.html')


# Route for object detection
# Route for object detection
@app.route('/detect', methods=['POST'])
def detect():
    try:
        # Process image with OpenCV
        data = request.get_json()
        image_data = base64.b64decode(data['image_data'])
        # Convert image_data to OpenCV format
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv.imdecode(nparr, cv.IMREAD_COLOR)
        # Perform object detection
        data = object_detector(frame)
        # Return result as JSON
        result = {
            'message': 'Detection result',
            'data': data
        }
        return jsonify(result)
    except Exception as e:
        # Return a 500 Internal Server Error with the error message
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
