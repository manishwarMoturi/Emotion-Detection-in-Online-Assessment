# Software Requirements Specification (SRS) for Emotion Detection Web Application

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for the Emotion Detection Web Application. The system is designed to provide emotion detection capabilities during practice sessions and live exams, along with exam and user management features for students, test takers, and administrators.

### 1.2 Scope
The application enables users to register and login with role-based access (admin, student, test taker). It supports emotion detection using a deep learning model, practice problems, exam scheduling, adaptive testing.

### 1.3 Definitions, Acronyms, and Abbreviations
- SRS: Software Requirements Specification
- UI: User Interface
- API: Application Programming Interface
- ML: Machine Learning
- CRUD: Create, Read, Update, Delete

## 2. Overall Description

### 2.1 Product Perspective
The system is a web-based application built with Flask, TensorFlow Keras for emotion detection, and MongoDB for data storage.

### 2.2 Product Functions
- User registration and authentication with roles (admin, student, test taker)
- Emotion detection from images during practice and live exams
- Practice problem management
- Exam scheduling and management
- Adaptive testing with emotion and performance-based difficulty adjustment
- Emotion history tracking for students
- Admin dashboard with reports and user management
- Live exam emotion detection and reporting feature
- Exam result submission and score calculation
- Export of exam reports in Excel format

### 2.3 User Classes and Characteristics
- Admin: Manages users, exams, and views reports
- Student: Practices problems, attends exams, emotion data tracked, participates in adaptive testing
- Test Taker: Assigns and monitors exams, receives emotion reports, manages exam lifecycle

### 2.4 Operating Environment
- Web browser for frontend
- Python 3.7+ backend with Flask
- MongoDB database
- TensorFlow and OpenCV for emotion detection

## 3. Specific Requirements

### 3.1 Functional Requirements

#### 3.1.1 User Management
- Users can register and login with roles
- Role-based access control enforced
- Password update functionality

#### 3.1.2 Emotion Detection
- Detect emotions from images during practice sessions and live exams
- Store emotion history per student
- Use a pre-trained deep learning model for emotion classification

#### 3.1.3 Practice Problems
- Students can view and solve practice problems
- Fetch practice problems by difficulty
- Adaptive testing adjusts question difficulty based on student performance and detected emotions

#### 3.1.4 Exam Management
- Admins and test takers can create, schedule, and manage exams
- Students can view and attend exams
- Exams have configurable parameters such as duration, max participants, max questions
- Exam lifecycle management: scheduled, ongoing, completed


#### 3.1.5 Adaptive Testing
- Students submit answers with selected options, time taken, and emotion counts
- System evaluates correctness and adjusts next question difficulty based on performance and emotions
- Difficulty levels: Easy, Medium, Hard
- Marks assigned based on difficulty and correctness
- Test completion detection based on max questions answered

#### 3.1.6 Live Exam Emotion Detection (New Feature)
- During live exams, the system captures student emotions continuously or at intervals
- After exam completion, the system calculates the most repeated emotion for each student
- The most repeated emotion is sent/reported to the test taker who assigned or started the exam
- The UI in `exams.html` includes the live emotion detection interface
- Backend APIs support storing and retrieving live exam emotion data

#### 3.1.7 Exam Result Submission and Reporting
- Students submit exam answers and scores are calculated and stored
- Average scores and pass rates are computed for exams
- Test takers can download exam reports in Excel format
- Admin dashboard provides analytics on exams, users, and emotion detection accuracy

#### 3.1.8 API Endpoints
- User authentication and registration APIs
- Emotion detection API accepting images and returning predicted emotions
- Practice problem retrieval APIs
- Exam CRUD APIs for test takers and admins
- Question CRUD APIs for managing exam questions
- Adaptive test answer submission API
- Exam start and end APIs
- Profile update APIs for students and test takers
- Admin APIs for user management, bulk actions, and data export

### 3.2 Non-Functional Requirements
- System should be responsive and user-friendly
- Emotion detection should be accurate and performant
- Adaptive testing should provide real-time difficulty adjustment
- Data privacy and security must be ensured, including secure session management and password hashing
- System should handle concurrent users and exams efficiently
- APIs should provide appropriate error handling and status codes

## 4. External Interface Requirements

### 4.1 User Interfaces
- Web pages for login, registration, dashboards, exams, practice, and reports
- Live emotion detection interface during exams
- Adaptive testing interface with real-time question updates
- Admin dashboard with analytics and user/exam management

### 4.2 Hardware Interfaces
- Webcam or camera device for capturing student images during live exams

### 4.3 Software Interfaces
- MongoDB for data storage
- TensorFlow and OpenCV for emotion detection
- Backend APIs for frontend communication

## 5. Other Requirements
- Secure session management
- Error handling and logging
- Data export functionality for reports

---

# Implementation Plan for Live Exam Emotion Detection Feature

1. Frontend (`exams.html`):
   - Integrate webcam access to capture student images during the exam.
   - Periodically send captured images to backend API for emotion detection.

2. Backend:
   - Create API endpoints to receive images and detect emotions using the existing model.
   - Store detected emotions linked to the student and exam session.
   - After exam completion, compute the most repeated emotion per student.
   - Provide API for test takers to retrieve emotion reports for assigned exams.

3. Database:
   - Extend MongoDB schema to store live exam emotion data.

4. Notifications:
   - Notify test takers with the emotion report after exam completion.

---
# Implementation Plan for Adaptive Testing Feature

1. Frontend:
   - Interface to present questions and capture answers with timing and emotion data.
   - Real-time updates of question difficulty based on backend response.

2. Backend:
   - API to submit answers with emotion counts and time taken.
   - Logic to evaluate correctness and adjust difficulty.
   - Store answers and calculate scores.

3. Database:
   - Collections for questions, answers, and exam results.

4. Reporting:
   - Provide exam results and analytics to students and test takers.

---

## 6. Database Design

The system uses MongoDB as the primary database. The main collections and their key fields are described below:

### 6.1 Users Collection
- _id: ObjectId
- username: string (unique)
- password: string (hashed)
- role: string (admin, student, testtaker)
- full_name: string
- email: string
- institution: string
- department: string
- student_id: string (for students)
- exams_conducted: int (for test takers)
- students_evaluated: int (for test takers)
- problems_solved: int (for students)
- exams_completed: int (for students)
- average_score: float
- active: boolean
- last_active: datetime

### 6.2 Exams Collection
- _id: ObjectId
- title: string
- date: string (formatted date)
- duration: int (minutes)
- max_participants: int
- min_questions: int
- max_questions: int
- description: string
- status: string (Scheduled, Ongoing, Completed, Draft)
- registered_students: int
- participated_students: int
- average_score: float
- pass_rate: float
- start_time: datetime
- end_time: datetime

### 6.3 Practice Problems Collection
- _id: ObjectId
- title: string
- description: string
- difficulty: string (Easy, Medium, Hard)
- problem_number: int

### 6.4 Questions Collection
- _id: ObjectId
- exam_id: ObjectId (reference to Exams)
- question_id: string (UUID)
- text: string
- options: list of strings
- correct_option: string
- difficulty: string (Easy, Medium, Hard)

### 6.5 Answers Collection
- _id: ObjectId
- exam_id: ObjectId
- username: string
- question_id: string
- selected_option: string
- time_taken: float (seconds)
- timed_out: boolean
- emotion_counts: dict (emotion label to count)
- difficulty: string
- streak: dict
- is_correct: boolean
- marks: int
- timestamp: datetime

### 6.6 Exam Results Collection
- _id: ObjectId
- exam_id: ObjectId
- username: string
- score: int
- max_score: int
- correct_answers: int
- total_questions: int
- percentage: float
- submitted_at: datetime

### 6.7 Emotion Analysis Collection
- _id: ObjectId
- label: string
- icon: string
- percentage: float
- alert: boolean
- alert_count: int

### 6.8 Emotion Trends Collection
- _id: ObjectId
- emotion: string
- percentage: float

### 6.9 Students Attention Collection
- _id: ObjectId
- initials: string
- name: string
- exam: string
- emotion: string

---
