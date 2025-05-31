import numpy as np
import cv2
import matplotlib.pyplot as plt
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from dotenv import load_dotenv
import os

#load_dotenv()
# ...rest of your code

# Emotion labels
EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised", "neutral"]

# Load the pre-trained model
#load_dotenv()  # Load environment variables from .env file

#EMOTION_MODEL_PATH = os.getenv('final22.h5')
# Update path if needed
model = load_model('final22.h5')
# Optional: compile (suppress warnings)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Display using matplotlib
def show_with_matplotlib(frame, title="Emotion Detection"):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    plt.axis('off')
    plt.title(title)
    plt.imshow(frame_rgb)
    plt.pause(0.001)
    plt.clf()

def detect_emotion(frame, face_cascade):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Process each face
    for (x, y, w, h) in faces:
        # Extract the face ROI
        roi = gray[y:y+h, x:x+w]
        
        # Resize to 48x48
        roi = cv2.resize(roi, (48, 48))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        
        # Make prediction
        preds = model.predict(roi, verbose=0)[0]
        emotion = EMOTIONS[preds.argmax()]
        return emotion, float(preds.max())
    
import numpy as np
import cv2
import matplotlib.pyplot as plt
from keras.models import load_model
from keras.preprocessing.image import img_to_array

# Emotion labels
EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised", "neutral"]

# Load the pre-trained model
#model_path = r'C:\EmotionDection\frontend\final22.h5'  # Update path if needed
model = load_model('final22.h5')

# Optional: compile (suppress warnings)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Display using matplotlib
def show_with_matplotlib(frame, title="Emotion Detection"):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    plt.axis('off')
    plt.title(title)
    plt.imshow(frame_rgb)
    plt.pause(0.001)
    plt.clf()

def detect_emotion(frame, face_cascade):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Process each face
    for (x, y, w, h) in faces:
        # Extract the face ROI
        roi = gray[y:y+h, x:x+w]
        
        # Resize to 48x48
        roi = cv2.resize(roi, (48, 48))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        
        # Make prediction
        preds = model.predict(roi, verbose=0)[0]
        emotion = EMOTIONS[preds.argmax()]
        return emotion, float(preds.max())
    

    return None, None
