# Object-Detection-and-Distance-Estimation-using-YoloV4

This repository contains an IoT-based object detection and distance estimation system using YOLOv4 (You Only Look Once). The system is divided into two main parts:
1. **Front-end:** Displays detected objects and estimated distances using a Flask application that fetches data from a Firebase Firestore database.
2. **Back-end:** Detects objects in real-time and estimates their distance using the YOLOv4 model. The back-end also updates the Firestore database and triggers alerts if objects are too close.

## Table of Contents
1. Features
2. Technologies Used
3. Setup Instructions
4. Front-end Setup
5. Back-end Setup
6. How It Works
   
## Features
- Real-time object detection using YOLOv4.
- Distance estimation of detected objects based on known object sizes.
- Alerts when objects are detected within a predefined distance threshold.
- Firebase integration for storing and displaying detection data.
- Flask front-end to visualize detected objects and their distances.

## Technologies Used
- Python: Main programming language.
- Flask: Web framework for the front-end.
- YOLOv4: Object detection algorithm.
- OpenCV: Image processing library.
- Firebase Firestore: Cloud database for storing detected object data.
- Firebase Admin SDK: For accessing Firestore in Python.
- Tkinter: GUI for running the back-end application.
- Pygame: For playing alert sounds.

## Setup Instructions
### Front-end Setup
1. Install the required packages:  
```
pip install flask firebase-admin
```
3. Configure Firebase:
- Add your Firebase credentials in chandu_key.json (this should contain your Firebase admin SDK key).
- Make sure the Firestore database is properly configured with a collection named `Object Detection and Distance Estimation.`
3. Run the Flask App:
```
python front_end.py
```

### Back-end Setup
1. Install the required packages:
```
pip install flask opencv-python numpy firebase-admin pygame pillow
```
3. Download YOLOv4 Model:
- Place the yolov4-tiny.weights and yolov4-tiny.cfg files in the root directory.
3. Configure Firebase:
- Add your Firebase credentials in chandu_key.json.
4. Run the Back-end Application:
```
python main.py
```

### Additional Files
- Classes File: The classes.txt file contains the names of objects that YOLOv4 can detect. It should be located in the root directory.
- Alert Sound: An alert_sound.mp3 file is played when an object crosses the distance threshold.
- Demo Video: The repository contains a demo video (demo.mp4) demonstrating the detection and distance estimation in action.

## How It Works
1. Front-end:
- The front-end Flask application fetches object detection data from the Firestore database and displays it in a web interface.
- Each detected object is listed with its timestamp and the estimated distance.
2. Back-end:
- The back-end application uses a live camera feed to detect objects using the YOLOv4 model.
- The distance to each detected object is calculated based on known object sizes.
- Detected objects within a certain distance threshold trigger an alert sound.
- Object detection data (name, distance, timestamp) is stored in the Firebase Firestore database.
3. Object Detection:
- The YOLOv4-tiny model is used for detecting objects.
- The system calculates distance using a combination of known object dimensions (e.g., person width, vehicle width) and the focal length.
4. Distance Calculation:
- Focal length is determined using reference images.
- Distances are calculated for each detected object based on their width in pixels and the known dimensions of the object.
