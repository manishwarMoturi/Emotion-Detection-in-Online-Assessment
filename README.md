# Emotion Detection System

A full-stack application for detecting and analyzing emotions during practice and exam sessions.

## Features

- Real-time emotion detection using computer vision
- Practice and exam session management
- Emotion tracking and analytics
- User authentication and authorization
- Session history and progress tracking

## Tech Stack

### Backend
- Django
- Django REST Framework
- PostgreSQL
- OpenCV
- TensorFlow/Keras

### Frontend
- React
- Material-UI
- Chart.js
- Axios

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL
- OpenCV
- TensorFlow

## Installation

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd emotion_detection_backend
pip install -r requirements.txt
```

3. Set up the database:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Install dependencies:
```bash
cd emotion_detection_frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## API Documentation

### Authentication
- POST /api/auth/login/ - User login
- POST /api/auth/register/ - User registration
- POST /api/auth/logout/ - User logout

### Practice Sessions
- GET /api/practice-sessions/ - List practice sessions
- POST /api/practice-sessions/ - Create practice session
- GET /api/practice-sessions/{id}/ - Get session details
- POST /api/practice-sessions/{id}/end_session/ - End session

### Exam Sessions
- GET /api/exam-sessions/ - List exam sessions
- POST /api/exam-sessions/ - Create exam session
- GET /api/exam-sessions/{id}/ - Get session details
- POST /api/exam-sessions/{id}/end_session/ - End session

## Testing

### Backend Tests
```bash
cd emotion_detection_backend
python manage.py test
```

### Frontend Tests
```bash
cd emotion_detection_frontend
npm test
```

## Deployment

1. Set up environment variables:
```bash
cp .env.example .env
```

2. Configure production settings:
- Update ALLOWED_HOSTS
- Set DEBUG=False
- Configure database settings
- Set up static files

3. Build frontend:
```bash
cd emotion_detection_frontend
npm run build
```

4. Deploy using your preferred hosting service (e.g., Heroku, AWS, DigitalOcean)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [AffectNet Dataset](https://github.com/siqueira-hc/Efficient-Facial-Feature-Learning-with-Wide-Ensemble-based-Convolutional-Neural-Networks)
- [FER2013 Dataset](https://www.kaggle.com/datasets/msambare/fer2013)
- TensorFlow.js team for the emotion detection model 