
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from dotenv import load_dotenv
import subprocess
import tempfile
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import io
import base64
from functools import wraps
from datetime import datetime
import cv2
from keras.preprocessing.image import img_to_array
from emotion_detection import detect_emotion
import random
from io import BytesIO
from pymongo import MongoClient
from bson.objectid import ObjectId

load_dotenv()  # Load environment variables from .env file

EMOTION_MODEL_PATH = os.getenv('EMOTION_MODEL_PATH')

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for local development over HTTP
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour


# Load emotion detection model
try:
    emotion_model = load_model(EMOTION_MODEL_PATH)
    #emotion_model = load_model(r'C:/EmotionDection/frontend/final22.h5')
    EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
except Exception as e:
    print(f"Error loading emotion model: {e}")
    emotion_model = None
    EMOTIONS = []

# File to store user data
USERS_FILE = 'users.json'

# File to store emotion history
EMOTION_HISTORY_FILE = 'emotion_history.json'

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB URI

db = client['emotion_detection']  # Database name
db_exams = db['exams']  # Collection name
problems_collection = db['practice_problems']  # Use the collection name already present in the database
db_users = db['users']  # New collection for users

# Create unique indexes and timestamps for collections
def create_indexes_and_timestamps():
    # Users collection: unique index on username
    db_users.create_index('username', unique=True)

    # Remove practice_questions collection and its indexes if exists
    if 'practice_questions' in db.list_collection_names():
        db.drop_collection('practice_questions')

    # Add created_at and updated_at fields on insert and update for all collections
    # This requires using MongoDB triggers or application-level code to set timestamps

# Call the function once at startup
create_indexes_and_timestamps()

from flask import request, jsonify

# Helper function to recursively convert ObjectId to string in dicts/lists
def convert_objectid_to_str(data):
    if isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            if isinstance(value, ObjectId):
                new_dict[key] = str(value)
            else:
                new_dict[key] = convert_objectid_to_str(value)
        return new_dict
    else:
        return data

@app.route('/api/get_question', methods=['GET'])
def get_question():
    difficulty = request.args.get('difficulty')
    if not difficulty:
        return jsonify({'status': 'error', 'message': 'Difficulty parameter is required'}), 400

    question = problems_collection.find_one({'difficulty': difficulty})
    if not question:
        return jsonify({'status': 'error', 'message': 'Question not found'}), 404

    # Remove MongoDB internal id before returning
    question.pop('_id', None)

    return jsonify({'status': 'success', 'title': question.get('title', ''), 'description': question.get('description', '')})

def load_emotion_history():
    if os.path.exists(EMOTION_HISTORY_FILE):
        with open(EMOTION_HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_emotion_history(history):
    with open(EMOTION_HISTORY_FILE, 'w') as f:
        json.dump(history, f)

# Remove read_users and write_users functions that use JSON file

# Remove users global variable loaded from JSON
emotion_history = load_emotion_history()

from flask import request, jsonify

def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'username' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
                else:
                    return redirect(url_for('index'))
            # Support role as list or string
            user_role = session.get('role')
            if isinstance(role, list):
                if user_role not in role:
                    if request.path.startswith('/api/'):
                        return jsonify({'status': 'error', 'message': 'Unauthorized role'}), 403
                    else:
                        return redirect(url_for('index'))
            else:
                if user_role != role:
                    if request.path.startswith('/api/'):
                        return jsonify({'status': 'error', 'message': 'Unauthorized role'}), 403
                    else:
                        return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

def preprocess_image(image_data):
    # Convert base64 to image
    image_data = base64.b64decode(image_data.split(',')[1])
    image = Image.open(io.BytesIO(image_data))
    
    # Resize and preprocess
    image = image.resize((48, 48))
    image = np.array(image.convert('L'))  # Convert to grayscale
    image = image.reshape(1, 48, 48, 1)
    image = image / 255.0  # Normalize
    
    return image

import cv2
import numpy as np
import base64
import io
from PIL import Image
from emotion_detection import detect_emotion as detect_emotion_func

@app.route('/api/detect_emotion/', methods=['POST'])
def detect_emotion():
    data = request.json
    image_data = data.get('image')

    if not image_data:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    if emotion_model is None:
        return jsonify({'status': 'error', 'message': 'Emotion detection model not loaded'}), 500

    try:
        # Load Haar cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Decode base64 image to OpenCV format
        img_data = base64.b64decode(image_data.split(',')[1])
        img_array = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Detect emotion using the function from emotion_detection.py
        emotion, confidence = detect_emotion_func(frame, face_cascade)

        if emotion is None:
            return jsonify({'status': 'error', 'message': 'No face detected'}), 400

        # Add debug logging
        print(f"Predicted emotion: {emotion} with confidence {confidence}")

        return jsonify({'status': 'success', 'emotion': emotion, 'confidence': confidence})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/get_emotion_history/')
@login_required('student')
def get_emotion_history():
    username = session['username']
    return jsonify({
        'status': 'success',
        'history': emotion_history.get(username, [])
    })

@app.route('/')
def index():
    # Always show login page regardless of session
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/student/dashboard')
@login_required('student')
def student_dashboard():
    practice_problems = fetch_practice_problems()
    # Fix: The template file is named 'student-dashboard.html' but the actual file is 'student-dashboard.html'
    # Check if the file exists, else rename or create it
    return render_template('student-dashboard.html', problems=practice_problems)

@app.route('/api/test/practice_problems_count')
def test_practice_problems_count():
    try:
        count = problems_collection.count_documents({})
        return jsonify({'status': 'success', 'count': count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/student/practice')
@login_required('student')
def practice():
    problem_id = request.args.get('problem_id')
    user_emotion_history = []
    error_message = None
    problem = None
    if problem_id:
        try:
            # Try to find by ObjectId
            if len(problem_id) == 24:
                problem = problems_collection.find_one({'_id': ObjectId(problem_id)})
            if not problem:
                # Try to find by numeric or string problem_number field
                try:
                    problem_number = int(problem_id)
                    problem = problems_collection.find_one({'problem_number': problem_number})
                except ValueError:
                    problem = problems_collection.find_one({'problem_number': problem_id})
            if problem:
                problem_data = {
                    'title': problem.get('title', ''),
                    'description': problem.get('description', ''),
                    'difficulty': problem.get('difficulty', '')
                }
                problem = problem_data
            else:
                error_message = "Problem not found."
        except Exception:
            error_message = "Error processing problem ID."
    else:
        error_message = "No problem selected."

    emotion_history_data = load_emotion_history()
    username = session.get('username')
    if username:
        user_emotion_history = emotion_history_data.get(username, [])

    return render_template('practice.html', problem=problem, emotion_history=user_emotion_history, error_message=error_message)

from bson.objectid import ObjectId

@app.route('/student/practice/<problem_id>')
@login_required('student')
def practice_problem(problem_id):
    try:
        problem = problems_collection.find_one({'_id': ObjectId(problem_id)})
        if problem:
            problem['_id'] = str(problem['_id'])
            return render_template('practice-problem.html', problem=problem)
        else:
            return "Problem not found", 404
    except Exception as e:
        return f"Invalid problem ID: {e}", 400

@app.route('/student/exams')
@login_required('student')
def exams():
    exams_data = fetch_exams()
    return render_template('exams.html', exams=exams_data)

@app.route('/student/exam/<int:exam_id>')
@login_required('student')
def exam_details(exam_id):
    return render_template('exam-details.html', exam_id=exam_id)

@app.route('/student/profile')
@login_required('student')
def profile():
    user_id = get_current_user_id()
    user = db_users.find_one({'username': user_id})
    if not user:
        return "User not found", 404

    profile_data = {
        'full_name': user.get('full_name', ''),
        'email': user.get('email', ''),
        'institution': user.get('institution', ''),
        'student_id': user.get('student_id', ''),
        'problems_solved': user.get('problems_solved', 0),
        'exams_completed': user.get('exams_completed', 0),
        'average_score': user.get('average_score', 0)
    }
    return render_template('profile.html', **profile_data)

@app.route('/api/login/', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password:
        return jsonify({
            'status': 'error',
            'message': 'Username and password are required'
        }), 400

    user = db_users.find_one({'username': username})
    if user and check_password_hash(user['password'], password) and user['role'] == role:
        session['username'] = username
        session['role'] = role
        session.permanent = True
        
        # Determine redirect URL based on role
        if role == 'admin':
            return jsonify({
                'status': 'success',
                'redirect': url_for('admin_dashboard')
            })
        elif role == 'student':
            return jsonify({
                'status': 'success',
                'redirect': url_for('student_dashboard')
            })
        else:
            return jsonify({
                'status': 'success',
                'redirect': url_for('testtaker_dashboard')
            })
    
    return jsonify({
        'status': 'error',
        'message': 'Invalid username, password, or role'
    }), 401

@app.route('/api/register/', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({
            'status': 'error',
            'message': 'All fields are required'
        }), 400

    existing_user = db_users.find_one({'username': username})
    if existing_user:
        return jsonify({
            'status': 'error',
            'message': 'Username already exists'
        }), 400

    hashed_password = generate_password_hash(password)
    new_user = {
        'username': username,
        'password': hashed_password,
        'role': role
    }
    result = db_users.insert_one(new_user)
    if result.inserted_id:
        return jsonify({
            'status': 'success',
            'message': 'Registration successful'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to register user'
        }), 500

@app.route('/api/execute/', methods=['POST'])
@login_required('student')
def execute_code():
    data = request.json
    code = data.get('code')
    language = data.get('language')

    if not code or not language:
        return jsonify({'status': 'error', 'message': 'Code or language not provided'}), 400

    try:
        if language == 'javascript':
            # Using Node.js to execute JS code
            result = subprocess.run(['node', '-e', code], capture_output=True, text=True)
        elif language == 'python':
            # Using Python to execute Python code
            result = subprocess.run(['python3', '-c', code], capture_output=True, text=True)
        else:
            return jsonify({'status': 'error', 'message': 'Unsupported language'}), 400

        if result.returncode == 0:
            return jsonify({'status': 'success', 'output': result.stdout})
        else:
            return jsonify({'status': 'error', 'message': result.stderr}), 400

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/get_question', methods=['GET'])
def get_question_api():
    difficulty = request.args.get('difficulty')

    if difficulty not in ['Easy', 'Medium', 'Hard']:
        return jsonify({'status': 'error', 'message': 'Invalid difficulty level'}), 400

    practice_questions_collection = db['practice_questions']
    question = practice_questions_collection.find_one({'difficulty': difficulty})

    if not question:
        return jsonify({'status': 'error', 'message': 'Question not found'}), 404

    # Remove MongoDB internal id before returning
    question.pop('_id', None)

    return jsonify(question)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Placeholder routes for other dashboards
@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    # Fetch total users count
    total_users = db_users.count_documents({})

    # Fetch active exams count (assuming status 'Scheduled' or 'Ongoing' means active)
    active_exams = db_exams.count_documents({'status': {'$in': ['Scheduled', 'Ongoing']}})

    # Fetch practice problems count
    practice_problems_count = problems_collection.count_documents({})

    # Practice problems completion rate placeholder (no data available)
    practice_problems_completion_rate = 0

    # Calculate exams scheduled today count
    from datetime import datetime
    today_str = datetime.now().strftime('%b %d, %Y')
    exams_scheduled_today = db_exams.count_documents({'date': today_str})

    # Calculate total participants across all exams
    total_participants = 0
    for exam in db_exams.find():
        total_participants += exam.get('participated_students', 0)

    # Average completion rate placeholder (no data available)
    average_completion_rate = 0

    # Fetch recent users sorted by last_active descending, limit 5
    recent_users_cursor = db_users.find().sort('last_active', -1).limit(5)
    recent_users = []
    for user in recent_users_cursor:
        recent_users.append({
            'user_id': str(user.get('_id')),
            'name': user.get('full_name', user.get('username', 'Unknown')),
            'role': user.get('role', 'N/A'),
            'status': 'Active' if user.get('active', True) else 'Inactive',
            'last_active': user.get('last_active', 'N/A')
        })

    # Fetch recent exams sorted by date descending, limit 5
    from datetime import datetime
    def parse_exam_date(exam):
        try:
            return datetime.strptime(exam.get('date', ''), '%b %d, %Y')
        except Exception:
            return datetime.min

    recent_exams_cursor = db_exams.find()
    recent_exams_list = list(recent_exams_cursor)
    recent_exams_list.sort(key=parse_exam_date, reverse=True)
    recent_exams = recent_exams_list[:5]

    # Pass counts, recent users, and recent exams to template
    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           active_exams=active_exams,
                           practice_problems_count=practice_problems_count,
                           practice_problems_completion_rate=practice_problems_completion_rate,
                           exams_scheduled_today=exams_scheduled_today,
                           total_participants=total_participants,
                           average_completion_rate=average_completion_rate,
                           recent_users=recent_users,
                           recent_exams=recent_exams)

@app.route('/admin/admin-users.html')
@login_required('admin')
def admin_users():
    return render_template('admin-users.html')

from flask import request

@app.route('/admin/exams')
@login_required('admin')
def admin_exams_page():
    from datetime import datetime
    # Get query parameters
    search_query = request.args.get('search', '').strip()
    filter_status = request.args.get('status', '').capitalize()
    filter_type = request.args.get('type', '').lower()
    page = int(request.args.get('page', 1))
    per_page = 10

    # Build query filter
    query_filter = {}
    if search_query:
        query_filter['title'] = {'$regex': search_query, '$options': 'i'}
    if filter_status:
        query_filter['status'] = filter_status
    if filter_type:
        query_filter['type'] = filter_type

    # Count total exams matching filter
    total_exams = db_exams.count_documents(query_filter)

    # Pagination calculation
    skip = (page - 1) * per_page

    # Fetch exams with filter and pagination
    exams_cursor = db_exams.find(query_filter).skip(skip).limit(per_page)
    exams_list = list(exams_cursor)

    # Calculate exam stats (without filters)
    active_exams = db_exams.count_documents({'status': {'$in': ['Scheduled', 'Ongoing']}})
    exams_scheduled_today = db_exams.count_documents({'date': datetime.now().strftime('%b %d, %Y')})
    total_participants = 0
    for exam in db_exams.find():
        total_participants += exam.get('participated_students', 0)
    average_completion_rate = 0  # Placeholder, no data available

    # Calculate total pages
    total_pages = (total_exams + per_page - 1) // per_page

    return render_template('admin-exams.html',
                           exams=exams_list,
                           active_exams=active_exams,
                           exams_scheduled_today=exams_scheduled_today,
                           total_participants=total_participants,
                           average_completion_rate=average_completion_rate,
                           search_query=search_query,
                           filter_status=filter_status,
                           filter_type=filter_type,
                           page=page,
                           total_pages=total_pages)

@app.route('/admin/admin-exams.html')
@login_required('admin')
def admin_exams():
    # This route is redundant and duplicates /admin/exams, so remove it
    # Redirect to /admin/exams or remove this function
    from flask import redirect, url_for
    return redirect(url_for('admin_exams_page'))

@app.route('/admin/reports')
@login_required('admin')
def admin_reports():
    try:
        # Fetch aggregated data for reports
        total_exams_taken = db_exams.count_documents({'status': 'Completed'})
        average_score_agg = db_exams.aggregate([
            {'$match': {'status': 'Completed'}},
            {'$group': {'_id': None, 'avgScore': {'$avg': '$average_score'}}}
        ])
        average_score = 0
        for doc in average_score_agg:
            avg = doc.get('avgScore', 0)
            if avg is None:
                average_score = 0
            else:
                average_score = round(avg, 2)

        active_users = db_users.count_documents({'active': True})

        # Placeholder for emotion detection accuracy - can be computed from logs or metrics collection
        emotion_detection_accuracy = 94.2

        # Additional detailed analytics data
        detailed_analytics = [
            {
                'metric': 'Total Exams Taken',
                'current_value': total_exams_taken,
                'previous_value': 1100,
                'change': total_exams_taken - 1100,
                'trend': 'up' if total_exams_taken >= 1100 else 'down'
            },
            {
                'metric': 'Average Score',
                'current_value': f"{average_score}%",
                'previous_value': '75.2%',
                'change': f"+{round(average_score - 75.2, 1)}%",
                'trend': 'up' if average_score >= 75.2 else 'down'
            },
            {
                'metric': 'Active Users',
                'current_value': active_users,
                'previous_value': 890,
                'change': active_users - 890,
                'trend': 'down' if active_users < 890 else 'up'
            },
            {
                'metric': 'Emotion Detection Accuracy',
                'current_value': f"{emotion_detection_accuracy}%",
                'previous_value': '92.8%',
                'change': f"+{round(emotion_detection_accuracy - 92.8, 1)}%",
                'trend': 'up' if emotion_detection_accuracy >= 92.8 else 'down'
            }
        ]

        report_data = {
            'total_exams_taken': total_exams_taken,
            'average_score': average_score,
            'active_users': active_users,
            'emotion_detection_accuracy': emotion_detection_accuracy,
            'detailed_analytics': detailed_analytics
        }

        return render_template('admin_reports.html', **report_data)
    except Exception as e:
        # Log the error and return the error message for debugging
        print(f"Error in admin_reports: {e}")
        return f"An error occurred while loading the reports: {e}", 500

# Admin API to get users list
@app.route('/api/admin/users', methods=['GET'])
@login_required('admin')
def admin_get_users():
    users = list(db_users.find())
    for user in users:
        user['_id'] = str(user['_id'])
        user['last_active'] = user.get('last_active', 'N/A')
        user['status'] = 'Active' if user.get('active', True) else 'Inactive'
    return jsonify({'status': 'success', 'users': users})

# Admin API to delete a user
@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@login_required('admin')
def admin_delete_user(user_id):
    try:
        result = db_users.delete_one({'_id': ObjectId(user_id)})
        if result.deleted_count == 1:
            return jsonify({'status': 'success', 'message': 'User deleted successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/users/bulk', methods=['POST'])
@login_required('admin')
def admin_bulk_user_actions():
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    action = data.get('action')

    if not user_ids or not isinstance(user_ids, list):
        return jsonify({'status': 'error', 'message': 'User IDs must be a non-empty list'}), 400

    if action not in ['activate', 'deactivate', 'delete']:
        return jsonify({'status': 'error', 'message': 'Invalid action'}), 400

    try:
        object_ids = [ObjectId(uid) for uid in user_ids]

        if action == 'delete':
            result = db_users.delete_many({'_id': {'$in': object_ids}})
            return jsonify({'status': 'success', 'message': f'Deleted {result.deleted_count} users'})

        elif action == 'activate':
            result = db_users.update_many({'_id': {'$in': object_ids}}, {'$set': {'active': True}})
            return jsonify({'status': 'success', 'message': f'Activated {result.modified_count} users'})

        elif action == 'deactivate':
            result = db_users.update_many({'_id': {'$in': object_ids}}, {'$set': {'active': False}})
            return jsonify({'status': 'success', 'message': f'Deactivated {result.modified_count} users'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

from io import BytesIO
from flask import send_file
import openpyxl

@app.route('/api/testtaker/exams/<exam_id>/report', methods=['GET'])
@login_required('testtaker')
def download_exam_report(exam_id):
    try:
        # Fetch exam data from database
        exam = db_exams.find_one({'_id': ObjectId(exam_id)})
        if not exam:
            return jsonify({'status': 'error', 'message': 'Exam not found'}), 404

        # Fetch exam results or evaluations related to this exam
        results = list(db_results.find({'exam_id': ObjectId(exam_id)}))

        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Exam Report"

        # Write header row
        headers = ['Student Name', 'Score', 'Status', 'Comments']
        ws.append(headers)

        # Write data rows
        for result in results:
            student_name = result.get('student_name', 'N/A')
            score = result.get('score', 'N/A')
            status = result.get('status', 'N/A')
            comments = result.get('comments', '')
            ws.append([student_name, score, status, comments])

        # Save workbook to a bytes buffer
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"exam_report_{exam_id}.xlsx"

        return send_file(output, attachment_filename=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Admin API to get exams list
@app.route('/api/admin/exams', methods=['GET'])
@login_required('admin')
def admin_get_exams():
    exams = list(db_exams.find())
    exams = convert_objectid_to_str(exams)
    for exam in exams:
        # Add participants count if not present
        if 'registered_students' not in exam:
            exam['registered_students'] = exam.get('participated_students', 0)
        # Add status badge class for frontend
        status = exam.get('status', '').lower()
        if status == 'scheduled':
            exam['status_badge'] = 'status-upcoming'
        elif status == 'ongoing':
            exam['status_badge'] = 'status-active'
        elif status == 'completed':
            exam['status_badge'] = 'status-completed'
        elif status == 'draft':
            exam['status_badge'] = 'status-draft'
        else:
            exam['status_badge'] = ''
    return jsonify({'status': 'success', 'exams': exams})

# API endpoint to export recent users and exams data for admin dashboard export button
@app.route('/api/admin/export_data', methods=['GET'])
@login_required('admin')
def admin_export_data():
    try:
        users = list(db_users.find())
        for user in users:
            user['_id'] = str(user['_id'])
            user['last_active'] = user.get('last_active', 'N/A')
            user['status'] = 'Active' if user.get('active', True) else 'Inactive'

        exams = list(db_exams.find())
        exams = convert_objectid_to_str(exams)
        for exam in exams:
            if 'registered_students' not in exam:
                exam['registered_students'] = exam.get('participated_students', 0)
            status = exam.get('status', '').lower()
            if status == 'scheduled':
                exam['status_badge'] = 'status-upcoming'
            elif status == 'ongoing':
                exam['status_badge'] = 'status-active'
            elif status == 'completed':
                exam['status_badge'] = 'status-completed'
            elif status == 'draft':
                exam['status_badge'] = 'status-draft'
            else:
                exam['status_badge'] = ''

        return jsonify({'status': 'success', 'users': users, 'exams': exams})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

 # New API endpoint to export recent users and exams data
# -@app.route('/api/admin/export_data', methods=['GET'])
# -@login_required('admin')
# -def admin_export_data():

# Admin API to delete an exam
@app.route('/api/admin/exams/<exam_id>', methods=['DELETE'])
@login_required('admin')
def admin_delete_exam(exam_id):
    try:
        result = db_exams.delete_one({'_id': ObjectId(exam_id)})
        if result.deleted_count == 1:
            return jsonify({'status': 'success', 'message': 'Exam deleted successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Exam not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/testtaker/dashboard')
@login_required('testtaker')
def testtaker_dashboard():
    # Fetch exams from database
    exams = list(db_exams.find())
    total_exams = len(exams)
    today_str = datetime.now().strftime('%b %d, %Y')
    scheduled_today = sum(1 for exam in exams if exam.get('date') == today_str)
    students_evaluated = sum(exam.get('participated_students', 0) for exam in exams)

    # Calculate evaluation increase compared to previous month
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Calculate students evaluated in current month
    current_month_evaluated = 0
    previous_month_evaluated = 0

    for exam in exams:
        exam_date_str = exam.get('date')
        if not exam_date_str:
            continue
        try:
            exam_date = datetime.strptime(exam_date_str, '%b %d, %Y')
        except ValueError:
            continue

        if exam_date.year == current_year and exam_date.month == current_month:
            current_month_evaluated += exam.get('participated_students', 0)
        elif exam_date.year == current_year and exam_date.month == (current_month - 1):
            previous_month_evaluated += exam.get('participated_students', 0)

    if previous_month_evaluated > 0:
        evaluation_increase = round(((current_month_evaluated - previous_month_evaluated) / previous_month_evaluated) * 100, 2)
    else:
        evaluation_increase = 0

    average_score = 0

    completed_exams = [exam for exam in exams if exam.get('status') == 'Completed']
    if completed_exams:
        total_score = sum(exam.get('average_score', 0) for exam in completed_exams)
        average_score = round(total_score / len(completed_exams), 2)

    upcoming_exams = [exam for exam in exams if exam.get('status') == 'Scheduled']
    ongoing_exams = [exam for exam in exams if exam.get('status') == 'Ongoing']

    # Fetch emotion data from database
    emotions_collection = db['emotion_analysis']
    emotions_data = list(emotions_collection.find())
    emotions = []
    for emotion_doc in emotions_data:
        emotions.append({
            'icon': emotion_doc.get('icon', ''),
            'percentage': emotion_doc.get('percentage', 0),
            'label': emotion_doc.get('label', ''),
            'alert': emotion_doc.get('alert', False),
            'alert_count': emotion_doc.get('alert_count', 0)
        })

    # Fetch students requiring attention from database
    students_collection = db['students_attention']
    students_requiring_attention_data = list(students_collection.find())
    students_requiring_attention = []
    for student in students_requiring_attention_data:
        students_requiring_attention.append({
            'id': str(student.get('_id')),
            'initials': student.get('initials', ''),
            'name': student.get('name', ''),
            'exam': student.get('exam', ''),
            'emotion': student.get('emotion', '')
        })

    # Fetch emotion trends from database
    emotion_trends_collection = db['emotion_trends']
    emotion_trends_data = list(emotion_trends_collection.find())
    emotion_trends = []
    for trend in emotion_trends_data:
        emotion_trends.append({
            'emotion': trend.get('emotion', ''),
            'percentage': trend.get('percentage', 0)
        })

    return render_template('testtaker_dashboard.html',
                           total_exams=total_exams,
                           scheduled_today=scheduled_today,
                           students_evaluated=students_evaluated,
                           evaluation_increase=evaluation_increase,
                           average_score=average_score,
                           upcoming_exams=upcoming_exams,
                           ongoing_exams=ongoing_exams,
                           completed_exams=completed_exams,
                           emotions=emotions,
                           students_requiring_attention=students_requiring_attention,
                           emotion_trends=emotion_trends)

@app.route('/testtaker/exams')
@login_required('testtaker')
def testtaker_exams():
    return render_template('testtaker_exams.html')

@app.route('/testtaker/results')
@login_required('testtaker')
def testtaker_results():
    # Fetch exams from database
    exams = list(db_exams.find())
    exams = convert_objectid_to_str(exams)
    total_exams = len(exams)
    completed_exams = [exam for exam in exams if exam.get('status') == 'Completed']
    completed_count = len(completed_exams)
    average_score = 0
    pass_rate = 0

    if completed_count > 0:
        total_score = sum(exam.get('average_score', 0) for exam in completed_exams)
        average_score = round(total_score / completed_count, 2)
        passing_exams = [exam for exam in completed_exams if exam.get('average_score', 0) >= 60]
        pass_rate = round((len(passing_exams) / completed_count) * 100, 2)

    # Emotion analysis data - fetch from DB collection 'emotion_analysis'
    emotions_collection = db['emotion_analysis']
    emotions_data = list(emotions_collection.find())

    # Aggregate emotion percentages
    emotions = []
    for emotion_doc in emotions_data:
        emotions.append({
            'icon': emotion_doc.get('icon', ''),
            'percentage': emotion_doc.get('percentage', 0),
            'label': emotion_doc.get('label', '')
        })

    # Prepare exam results data for table
    exam_results = []
    for exam in completed_exams:
        exam_results.append({
            'title': exam.get('title', 'N/A'),
            'date': exam.get('date', 'N/A'),
            'participants': f"{exam.get('participated_students', 0)}/{exam.get('max_participants', 0)}",
            'average_score': exam.get('average_score', 0),
            'pass_rate': pass_rate,
            'dominant_emotion': 'Happy',  # Stub, can be computed
            'dominant_emotion_icon': '😊',
            'dominant_emotion_percentage': 60  # Stub
        })

    return render_template('testtaker_results.html',
                           average_score=average_score,
                           total_exams=total_exams,
                           pass_rate=pass_rate,
                           emotions=emotions,
                           exam_results=exam_results)

from flask import request, jsonify
from bson.objectid import ObjectId

@app.route('/api/testtaker/exams', methods=['GET', 'POST', 'DELETE'])
@login_required('testtaker')
def api_testtaker_exams():
    if request.method == 'GET':
        exams = list(db_exams.find())
        exams = convert_objectid_to_str(exams)
        return jsonify({'status': 'success', 'exams': exams})
    elif request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        date = data.get('date')
        duration = data.get('duration')
        max_participants = data.get('max_participants')
        min_questions = data.get('min_questions')
        max_questions = data.get('max_questions')
        description = data.get('description')
        questions = data.get('questions', [])

        if not title or not date or not duration or not max_participants:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        new_exam = {
            'title': title,
            'date': date,
            'duration': duration,
            'max_participants': int(max_participants),
            'min_questions': int(min_questions) if min_questions is not None else None,
            'max_questions': int(max_questions) if max_questions is not None else None,
            'description': description,
            'status': 'Scheduled',
            'registered_students': 0
        }

        result = db_exams.insert_one(new_exam)
        if result.inserted_id:
            exam_id = result.inserted_id
            # Insert questions into a separate collection with exam_id reference
            import uuid
            questions_to_insert = []
            for question in questions:
                question_doc = {
                'exam_id': exam_id,
                'question_id': question.get('question_id') or str(uuid.uuid4()),  # Auto-generate UUID if missing
                'text': question.get('text'),
                'options': question.get('options'),
                'correct_option': question.get('correct_option'),
                'difficulty': question.get('difficulty')
            }

                questions_to_insert.append(question_doc)
            if questions_to_insert:
                db['questions'].insert_many(questions_to_insert)
            return jsonify({'status': 'success', 'message': 'Exam and questions created successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to create exam'}), 500
    elif request.method == 'DELETE':
        data = request.get_json()
        exam_id = data.get('exam_id')
        if not exam_id:
            return jsonify({'status': 'error', 'message': 'Exam ID is required'}), 400
        try:
            result = db_exams.delete_one({'_id': ObjectId(exam_id)})
            if result.deleted_count == 1:
                return jsonify({'status': 'success', 'message': 'Exam deleted successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Exam not found'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/testtaker/exams/<exam_id>/start', methods=['POST'])
@login_required('testtaker')
def start_exam(exam_id):
    try:
        exam = db_exams.find_one({'_id': ObjectId(exam_id)})
        if not exam:
            return jsonify({'status': 'error', 'message': 'Exam not found'}), 404

        if exam.get('status') == 'Ongoing':
            return jsonify({'status': 'error', 'message': 'Exam already started'}), 400

        db_exams.update_one({'_id': ObjectId(exam_id)}, {'$set': {'status': 'Ongoing', 'start_time': datetime.now().isoformat()}})
        return jsonify({'status': 'success', 'message': 'Exam started successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Remove read_users and write_users functions that use JSON file
# Remove users global variable loaded from JSON

@app.route('/testtaker/profile')
@login_required('testtaker')
def testtaker_profile():
    user_id = get_current_user_id()
    user = db_users.find_one({'username': user_id})
    if not user:
        return "User not found", 404

    initials = ''.join([name[0] for name in user.get('full_name', 'Unknown User').split()]).upper() if user.get('full_name') else 'UU'

    profile_data = {
        'initials': initials,
        'full_name': user.get('full_name', 'Unknown User'),
        'email': user.get('email', 'N/A'),
        'institution': user.get('institution', 'University of Technology'),
        'department': user.get('department', 'Computer Science'),
        'exams_conducted': user.get('exams_conducted', 0),
        'students_evaluated': user.get('students_evaluated', 0),
        'average_score': user.get('average_score', 0)
    }
    # Fix: Render the correct template file 'profile.html' instead of 'testtaker_profile.html'
    return render_template('testtaker_profile.html', **profile_data)

@app.route('/api/testtaker/profile/update', methods=['POST'])
@login_required('testtaker')
def update_profile():
    user_id = get_current_user_id()
    data = request.get_json()
    user = db_users.find_one({'username': user_id})
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    update_fields = {}
    for field in ['full_name', 'email', 'institution', 'department']:
        if field in data:
            update_fields[field] = data[field]

    if update_fields:
        db_users.update_one({'username': user_id}, {'$set': update_fields})
        return jsonify({'status': 'success', 'message': 'Profile updated successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'No valid fields to update'}), 400

@app.route('/api/student/profile/update', methods=['POST'])
@login_required('student')
def update_student_profile():
    user_id = get_current_user_id()
    data = request.get_json()
    user = db_users.find_one({'username': user_id})
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    update_fields = {}
    for field in ['full_name', 'email', 'institution', 'department']:
        if field in data:
            update_fields[field] = data[field]

    if update_fields:
        db_users.update_one({'username': user_id}, {'$set': update_fields})
        return jsonify({'status': 'success', 'message': 'Profile updated successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'No valid fields to update'}), 400

from werkzeug.security import generate_password_hash

@app.route('/api/testtaker/profile/password', methods=['POST'])
@login_required('testtaker')
def update_password():
    user_id = get_current_user_id()
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'status': 'error', 'message': 'Current and new passwords are required'}), 400

    user = db_users.find_one({'username': user_id})
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    if not check_password_hash(user['password'], current_password):
        return jsonify({'status': 'error', 'message': 'Current password is incorrect'}), 400

    new_hashed_password = generate_password_hash(new_password)
    db_users.update_one({'username': user_id}, {'$set': {'password': new_hashed_password}})

    return jsonify({'status': 'success', 'message': 'Password updated successfully'})

def get_current_user_id():
    return session.get('username')

# Function to fetch exams from MongoDB
def fetch_exams():
    exams = list(db_exams.find())
    # Convert status to lowercase for frontend consistency
    for exam in exams:
        if 'status' in exam and isinstance(exam['status'], str):
            exam['status'] = exam['status'].lower()
    # Add user score and user exam status from exam_results if available
    username = session.get('username')
    if username:
        for exam in exams:
            exam_result = db['exam_results'].find_one({'exam_id': exam['_id'], 'username': username})
            if exam_result:
                exam['score'] = exam_result.get('percentage', 0)
                exam['user_status'] = exam_result.get('status', 'not_started')
            else:
                exam['score'] = None
                exam['user_status'] = 'not_started'
    return exams

# Function to fetch practice problems from MongoDB
def fetch_practice_problems():
    problems = list(problems_collection.find())
    # Convert ObjectId to string for template usage
    for problem in problems:
        problem['_id'] = str(problem['_id'])
    return problems

from flask import render_template

@app.route('/testtaker/exam-monitor/<exam_id>')
@login_required('testtaker')
def exam_monitor(exam_id):
    try:
        # Fetch exam details from database
        exam = db_exams.find_one({'_id': ObjectId(exam_id)})
        if not exam:
            return "Exam not found", 404
        exam['_id'] = str(exam['_id'])
        # Render the exam monitoring page
        return render_template('exam_monitor.html', exam=exam)
    except Exception as e:
        return f"Error loading exam monitor: {str(e)}", 500

@app.route('/attempt_exam/<exam_id>')
@login_required('student')
def attempt_exam(exam_id):
    exam = db_exams.find_one({'_id': ObjectId(exam_id)})
    if not exam:
        return "Exam not found", 404
    exam['_id'] = str(exam['_id'])
    try:
        min_questions = int(exam.get('min_questions', 0))
    except (ValueError, TypeError):
        min_questions = 0
    try:
        max_questions = int(exam.get('max_questions', 9999))
    except (ValueError, TypeError):
        max_questions = 9999
    return render_template('attempt_exam.html', exam=exam, min_questions=min_questions, max_questions=max_questions)

@app.route('/api/testtaker/exams/<exam_id>/end', methods=['POST'])
def end_exam(exam_id):
    # Fetch the exam document from MongoDB
    exam = db_exams.find_one({'_id': ObjectId(exam_id)})
    
    if not exam:
        return jsonify({'status': 'error', 'message': 'Exam not found'}), 404
    
    # If exam is already completed, return success immediately (idempotent)
    if exam.get('status') == 'Completed':
        return jsonify({'status': 'success', 'message': 'Exam already completed'})
    
    # Only allow ending if exam is ongoing
    if exam.get('status') != 'Ongoing':
        return jsonify({'status': 'error', 'message': 'Exam is not ongoing'}), 400
    
    # Update exam status to Completed and set end time
    db_exams.update_one(
        {'_id': ObjectId(exam_id)},
        {
            '$set': {
                'status': 'Completed',
                'end_time': datetime.now().isoformat()
            }
        }
    )
    
    return jsonify({'status': 'success', 'message': 'Exam ended successfully'})

# New API endpoints for questions CRUD operations

from flask import request

@app.route('/api/testtaker/questions/<exam_id>', methods=['GET'])
@login_required(['student', 'testtaker'])
def get_questions(exam_id):
    try:
        exclude_ids = request.args.getlist('exclude')
        difficulty = request.args.get('difficulty')
        query = {'$or': [
            {'exam_id': ObjectId(exam_id)},
            {'exam_id': exam_id}
        ]}
        if difficulty:
            query['difficulty'] = difficulty
        if exclude_ids:
            query['question_id'] = {'$nin': exclude_ids}
        questions = list(db['questions'].find(query))
        for q in questions:
            q['_id'] = str(q['_id'])
            q['exam_id'] = str(q['exam_id'])
        return jsonify({'status': 'success', 'questions': questions})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/testtaker/questions/<question_id>', methods=['PUT'])
@login_required('testtaker')
def update_question(question_id):
    data = request.get_json()
    try:
        update_fields = {}
        for field in ['text', 'options', 'correct_option', 'difficulty']:
            if field in data:
                update_fields[field] = data[field]
        if not update_fields:
            return jsonify({'status': 'error', 'message': 'No valid fields to update'}), 400
        result = db['questions'].update_one({'_id': ObjectId(question_id)}, {'$set': update_fields})
        if result.matched_count == 0:
            return jsonify({'status': 'error', 'message': 'Question not found'}), 404
        return jsonify({'status': 'success', 'message': 'Question updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/testtaker/questions/<question_id>', methods=['DELETE'])
@login_required('testtaker')
def delete_question(question_id):
    try:
        result = db['questions'].delete_one({'_id': ObjectId(question_id)})
        if result.deleted_count == 0:
            return jsonify({'status': 'error', 'message': 'Question not found'}), 404
        return jsonify({'status': 'success', 'message': 'Question deleted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/testtaker/questions', methods=['POST'])
@login_required('testtaker')
def create_question():
    data = request.get_json()
    required_fields = ['exam_id', 'text', 'options', 'correct_option', 'difficulty']
    if not all(field in data for field in required_fields):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    try:
        question_doc = {
            'exam_id': ObjectId(data['exam_id']),
            'text': data['text'],
            'options': data['options'],
            'correct_option': data['correct_option'],
            'difficulty': data['difficulty']
        }
        result = db['questions'].insert_one(question_doc)
        if result.inserted_id:
            return jsonify({'status': 'success', 'message': 'Question created successfully', 'question_id': str(result.inserted_id)})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to create question'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

from flask import request, jsonify, session
from bson.objectid import ObjectId
from datetime import datetime

@app.route('/api/adaptive_test/submit_answer', methods=['POST'])
@login_required(['student'])
def submit_answer():
    from collections import Counter

    data = request.get_json()
    exam_id = data.get('exam_id')
    question_id = data.get('question_id')
    selected_option = data.get('selected_option')
    time_taken = data.get('time_taken')
    timed_out = data.get('timed_out', False)
    emotion_counts = data.get('emotion_counts', {})
    difficulty_raw = data.get('difficulty')  # "Easy", "Medium", etc.
    streak = data.get('streak', {})

    if not exam_id or not question_id or selected_option is None or time_taken is None or difficulty_raw is None:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        exam_obj_id = ObjectId(exam_id)
        username = session['username']
        difficulty = difficulty_raw.lower()

        # Fetch the question
        question = db['questions'].find_one({'question_id': question_id})
        correct_option = question.get('correct_option') if question else None
        is_correct = question and str(selected_option) == str(correct_option)

        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else 'neutral'
        print(f"🧠 Evaluation: Correct={is_correct}, Time={time_taken}s, Emotion={dominant_emotion}")

        # Adaptive Difficulty Logic
        old_difficulty = difficulty
        if is_correct and time_taken <= 60 and dominant_emotion in ['happy', 'neutral']:
            difficulty = {'easy': 'medium', 'medium': 'hard', 'hard': 'hard'}[difficulty]
        elif not is_correct and time_taken > 60 and dominant_emotion in ['sad', 'angry', 'disgust']:
            difficulty = {'hard': 'medium', 'medium': 'easy', 'easy': 'easy'}[difficulty]
        elif not is_correct and dominant_emotion in ['fear', 'surprise']:
            difficulty = {'hard': 'medium', 'medium': 'easy', 'easy': 'easy'}[difficulty]
        elif is_correct and dominant_emotion == 'happy':
            difficulty = {'easy': 'hard', 'medium': 'hard', 'hard': 'hard'}[difficulty]
        elif is_correct and dominant_emotion == 'sad':
            difficulty = 'easy'
        elif time_taken > 60 and dominant_emotion == 'sad':
            difficulty = {'hard': 'medium', 'medium': 'easy', 'easy': 'easy'}[difficulty]
        elif time_taken > 60 and dominant_emotion == 'happy':
            difficulty = {'easy': 'medium', 'medium': 'hard', 'hard': 'hard'}[difficulty]
        # Otherwise, maintain difficulty

        print(f"🎯 Difficulty: {old_difficulty} → {difficulty}")

        final_difficulty = difficulty.title()
        difficulty_marks = {'easy': 1, 'medium': 2, 'hard': 3}
        marks = difficulty_marks.get(difficulty, 1) if is_correct else 0

        # Save answer
        db['answers'].insert_one({
            'exam_id': exam_obj_id,
            'username': username,
            'question_id': question_id,
            'selected_option': selected_option,
            'time_taken': time_taken,
            'timed_out': timed_out,
            'emotion_counts': emotion_counts,
            'difficulty': final_difficulty,
            'streak': streak,
            'is_correct': is_correct,
            'marks': marks,
            'timestamp': datetime.utcnow()
        })

        # Get already answered question IDs
        answered_question_ids = db['answers'].distinct('question_id', {
            'exam_id': exam_obj_id,
            'username': username
        })

        # Fetch next question with the updated difficulty
        next_questions = list(db['questions'].find({
            'exam_id': exam_obj_id,
            'difficulty': final_difficulty,
            'question_id': {'$nin': answered_question_ids}
        }))

        # Fallback: search other difficulties if none available
        if not next_questions:
            for alt in ['Easy', 'Medium', 'Hard']:
                if alt == final_difficulty:
                    continue
                fallback_questions = list(db['questions'].find({
                    'exam_id': exam_obj_id,
                    'difficulty': alt,
                    'question_id': {'$nin': answered_question_ids}
                }))
                if fallback_questions:
                    next_questions = fallback_questions
                    final_difficulty = alt
                    break

        if next_questions:
            next_question = next_questions[0]
            next_question['_id'] = str(next_question['_id'])
            next_question['exam_id'] = str(next_question['exam_id'])

            return jsonify({
                'status': 'success',
                'next_question': next_question,
                'testComplete': False,
                'difficulty': final_difficulty
            })
        else:
            return jsonify({
                'status': 'success',
                'next_question': None,
                'testComplete': True,
                'difficulty': final_difficulty
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

    
@app.route('/api/exam/<exam_id>/submit', methods=['POST'])
@login_required('student')
def submit_exam_and_store_score(exam_id):
    username = session['username']
    exam_obj_id = ObjectId(exam_id)

    try:
        # Fetch all answers by student for this exam
        answers = list(db['answers'].find({
            'exam_id': exam_obj_id,
            'username': username
        }))

        total_score = sum(ans.get('marks', 0) for ans in answers)
        max_score = sum(3 for _ in answers)
        correct_answers = sum(1 for ans in answers if ans.get('is_correct'))
        total_questions = len(answers)
        percentage = round((total_score / max_score) * 100, 2) if max_score else 0

        # Upsert result for this student and exam
        db['exam_results'].update_one(
            {'exam_id': exam_obj_id, 'username': username},
            {'$set': {
                'score': total_score,
                'max_score': max_score,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'percentage': percentage,
                'submitted_at': datetime.utcnow()
            }},
            upsert=True
        )

        # Increment participated_students count for the exam only if this is the first submission
        if db['exam_results'].count_documents({'exam_id': exam_obj_id, 'username': username}) == 1:
            db_exams.update_one({'_id': exam_obj_id}, {'$inc': {'participated_students': 1}})

        # Calculate and update average score and pass rate for the exam
        exam_results = list(db['exam_results'].find({'exam_id': exam_obj_id}))
        if exam_results:
            total_scores = sum(result.get('percentage', 0) for result in exam_results)
            average_score = round(total_scores / len(exam_results), 2)
            passing_count = sum(1 for result in exam_results if result.get('percentage', 0) >= 60)
            pass_rate = round((passing_count / len(exam_results)) * 100, 2)

            db_exams.update_one({'_id': exam_obj_id}, {'$set': {'average_score': average_score, 'pass_rate': pass_rate}})

        return jsonify({'status': 'success', 'message': 'Score submitted', 'score': total_score, 'percentage': percentage})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
