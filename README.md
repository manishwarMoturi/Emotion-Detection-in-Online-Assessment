<<<<<<< HEAD
# Emotion Detection Web Application

This project is a Flask-based web application for emotion detection using a pre-trained deep learning model. It provides features for students, test takers, and administrators to manage exams, practice problems, and track emotion history during practice sessions.

## Features

- Emotion detection from images using a TensorFlow Keras model.
- User authentication and role-based access (admin, student, test taker).
- Practice problems and exams management.
- Adaptive testing with real-time difficulty adjustment based on student performance and detected emotions.
- Live exam emotion detection capturing student emotions during exams and reporting to test takers.
- Emotion history tracking for students.
- Admin dashboard with reports and user management.
- MongoDB integration for data storage, including users, exams, questions, answers, and emotion data.
- API endpoints for user management, emotion detection, adaptive testing, exam lifecycle, and reporting.

## Installation

1. Clone the repository.

2. Ensure you have Python 3.7 or higher installed.

3. Install the required Python packages:

```bash
pip install -r requirements.txt
```

4. Make sure MongoDB is installed and running on your machine. The app connects to MongoDB at `mongodb://localhost:27017/` by default. Update the connection string in `frontend/app.py` if needed.

5. Place the pre-trained model files (`final22.h5`) in the `frontend/` directory or update the path in the code accordingly.

## Running the Application

Run the Flask app from the `frontend` directory:

```bash
python app.py
```

The app will be available at `http://127.0.0.1:5000/`.

## Project Structure

- `frontend/app.py`: Main Flask application.
- `frontend/emotion_detection.py`: Emotion detection model and utilities.
- `frontend/insert_sample_exams.py`: Script to insert sample exams and practice problems into MongoDB.
- `frontend/templates/`: HTML templates for the web pages.
- `frontend/static/`: Static files including JavaScript, CSS, and images.
- `requirements.txt`: Python dependencies.

## Notes

- The app uses TensorFlow and Keras for emotion detection.
- MongoDB is required for storing users, exams, practice problems, questions, answers, and emotion data.
- OpenCV and Pillow are used for image processing.
- The app includes role-based access control for different user types.
- Adaptive testing adjusts question difficulty dynamically based on student responses and emotions.
- Live exam emotion detection captures and reports student emotions during exams to test takers.
- Comprehensive API endpoints support frontend-backend communication and data management.

## License

This project is licensed under the MIT License.
python app.py
pip install -r requirements.txt


=======
# Emotion Detection Web Application

This project is a Flask-based web application for emotion detection using a pre-trained deep learning model. It provides features for students, test takers, and administrators to manage exams, practice problems, and track emotion history during practice sessions.

## Features

- Emotion detection from images using a TensorFlow Keras model.
- User authentication and role-based access (admin, student, test taker).
- Practice problems and exams management.
- Adaptive testing with real-time difficulty adjustment based on student performance and detected emotions.
- Live exam emotion detection capturing student emotions during exams and reporting to test takers.
- Emotion history tracking for students.
- Admin dashboard with reports and user management.
- MongoDB integration for data storage, including users, exams, questions, answers, and emotion data.
- API endpoints for user management, emotion detection, adaptive testing, exam lifecycle, and reporting.

## Installation

1. Clone the repository.

2. Ensure you have Python 3.7 or higher installed.

3. Install the required Python packages:

```bash
pip install -r requirements.txt
```

4. Make sure MongoDB is installed and running on your machine. The app connects to MongoDB at `mongodb://localhost:27017/` by default. Update the connection string in `frontend/app.py` if needed.

5. Place the pre-trained model files (`final22.h5`) in the `frontend/` directory or update the path in the code accordingly.

## Running the Application

Run the Flask app from the `frontend` directory:

```bash
python app.py
```

The app will be available at `http://127.0.0.1:5000/`.

## Project Structure

- `frontend/app.py`: Main Flask application.
- `frontend/emotion_detection.py`: Emotion detection model and utilities.
- `frontend/insert_sample_exams.py`: Script to insert sample exams and practice problems into MongoDB.
- `frontend/templates/`: HTML templates for the web pages.
- `frontend/static/`: Static files including JavaScript, CSS, and images.
- `requirements.txt`: Python dependencies.

## Notes

- The app uses TensorFlow and Keras for emotion detection.
- MongoDB is required for storing users, exams, practice problems, questions, answers, and emotion data.
- OpenCV and Pillow are used for image processing.
- The app includes role-based access control for different user types.
- Adaptive testing adjusts question difficulty dynamically based on student responses and emotions.
- Live exam emotion detection captures and reports student emotions during exams to test takers.
- Comprehensive API endpoints support frontend-backend communication and data management.

## License

This project is licensed under the MIT License.
python app.py
pip install -r requirements.txt


>>>>>>> 13fc31d (Initial Commit)
python "C:\EmotionDection\frontend\app.py"