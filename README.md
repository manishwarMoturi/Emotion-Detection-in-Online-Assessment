# Emotion-Detection-in-Online-Assessment
# Emotion Detection Coding Platform

A web-based platform for emotion detection and coding practice, featuring role-based access for students, test takers, and administrators.

## Features

- **Role-Based Access Control**
  - Student Dashboard
  - Test Taker Dashboard
  - Admin Dashboard
- **Emotion Detection**
  - Real-time emotion analysis
  - Practice sessions
  - Test environment
- **User Management**
  - Secure login system
  - Profile management
  - Progress tracking

## Project Structure

```
emotion-detection/
├── static/
│   ├── styles/
│   └── scripts/
├── templates/
│   ├── index.html
│   ├── student-dashboard.html
│   ├── testtaker-dashboard.html
│   └── admin-dashboard.html
├── models/
├── src/
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Web browser with JavaScript enabled
- Webcam (for emotion detection features)

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd emotion-detection
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Login
- Use the role selector to choose your role (Student, Test Taker, or Admin)
- Enter your credentials
- Click "Sign In" to access your dashboard

### Student Dashboard
- Access practice sessions
- View progress
- Take tests

### Test Taker Dashboard
- Take scheduled tests
- View results
- Access practice materials

### Admin Dashboard
- Manage users
- Create and schedule tests
- Monitor system performance

## Technologies Used

- Frontend:
  - HTML5
  - CSS3
  - JavaScript
  - TensorFlow.js (for emotion detection)

- Backend:
  - Python
  - Flask
  - OpenCV
  - TensorFlow

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [AffectNet Dataset](https://github.com/siqueira-hc/Efficient-Facial-Feature-Learning-with-Wide-Ensemble-based-Convolutional-Neural-Networks)
- [FER2013 Dataset](https://www.kaggle.com/datasets/msambare/fer2013)
- TensorFlow.js team for the emotion detection model 
