// Get references to the video element and canvas element
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startButton = document.getElementById('startButton');
const captureButton = document.getElementById('captureButton');

// Function to start the camera
async function startCamera() {
    try {
        // Get access to the camera stream
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        // Set the video source to the camera stream
        video.srcObject = stream;
        // Wait for the video metadata to load to ensure proper dimensions
        await video.play(); // Auto-plays the video to trigger the 'loadedmetadata' event
        // Process the video stream with algorithm
        processVideo();
    } catch (error) {
        console.error('Error accessing the camera: ', error);
        alert('Error accessing the camera. Please make sure you have granted permission to access the camera.');
    }
}

// Function to capture a photo from the video stream
function capturePhoto() {
    // Draw the current frame of the video onto the canvas
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
}

// Function to process the video stream with algorithm
async function processVideo() {
    try {
        const stream = video.srcObject;
        const track = stream.getVideoTracks()[0];
        const imageCapture = new ImageCapture(track);

        // Continuously capture frames and process them
        setInterval(async () => {
            try {
                const frame = await imageCapture.grabFrame();
                const canvas = document.createElement('canvas');
                const tempContext = canvas.getContext('2d'); // Rename the context variable
                canvas.width = frame.width;
                canvas.height = frame.height;
                tempContext.drawImage(frame, 0, 0);
                const imageData = tempContext.getImageData(0, 0, frame.width, frame.height);

                // Send image data as JSON
                const response = await fetch('http://127.0.0.1:5000/detect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ image_data: Array.from(imageData.data) })
                });

                if (!response.ok) {
                    throw new Error(`Failed to send captured frame: ${response.status} ${response.statusText}`);
                }

                const result = await response.json();
                console.log(result);

                const context = canvas.getContext('2d');
                context.clearRect(0, 0, canvas.width, canvas.height);
                result.data.forEach(([_, boundingBox, __]) => {
                    context.beginPath();
                    context.rect(boundingBox[0], boundingBox[1], boundingBox[2], boundingBox[3]);
                    context.lineWidth = 2;
                    context.strokeStyle = 'green';
                    context.stroke();
                });
            } catch (error) {
                console.error('Error processing the frame: ', error);
            }
        }, 1000); // Adjust the interval as needed
    } catch (error) {
        console.error('Error processing the video: ', error);
        alert('Error processing the video. Please check the console for details.');
    }
}


// Convert frame to Blob
async function frameToBlob(frame) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = frame.width;
    canvas.height = frame.height;
    context.drawImage(frame, 0, 0);
    return new Promise((resolve, reject) => {
        canvas.toBlob(resolve, 'image/png');
    });
}

// Add event listener for the start button if it exists
if (startButton) {
    startButton.addEventListener('click', function() {
        startCamera();
    });
} else {
    console.error('Start button not found.');
}

// Add event listener for the capture button if it exists
if (captureButton) {
    captureButton.addEventListener('click', capturePhoto);
} else {
    console.error('Capture button not found.');
}
