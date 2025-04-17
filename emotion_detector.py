import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import os

def detect_emotions():
    try:
        # Check if model file exists
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'final22.h5')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        print(f"Loading model from: {model_path}")
        # Load pre-trained model
        model = load_model(model_path)
        print("Model loaded successfully")

        # Emotion labels based on FER2013
        emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

        # Load OpenCV's face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if face_cascade.empty():
            raise Exception("Failed to load face cascade classifier")

        # Start webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Could not open webcam")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            for (x, y, w, h) in faces:
                try:
                    # Draw rectangle around face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)

                    # Extract face ROI
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_resized = cv2.resize(roi_gray, (48, 48))
                    roi = roi_resized.astype("float") / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)

                    # Predict emotion
                    preds = model.predict(roi, verbose=0)[0]
                    label = emotion_labels[np.argmax(preds)]
                    confidence = np.max(preds)

                    # Display label and confidence
                    text = f"{label} ({confidence*100:.1f}%)"
                    cv2.putText(frame, text, (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                except Exception as e:
                    print(f"Error processing face: {str(e)}")
                    continue

            # Show the frame
            cv2.imshow("Emotion Detection", frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Cleanup
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()