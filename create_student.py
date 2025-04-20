import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emotion_detection.settings')
django.setup()

# Import models
from emotion_app.models import User

# Create a student user
try:
    # Check if user already exists
    if User.objects.filter(username='student').exists():
        print("Student user already exists.")
        student_user = User.objects.get(username='student')
        student_user.set_password('student123')  # Reset password
        student_user.save()
        print("Password reset to 'student123'")
    else:
        # Create a new student user
        student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='student123',
            first_name='Student',
            last_name='User',
            role='student',
            current_practice_difficulty='easy',
            practice_happy_streak=2,
            practice_sad_streak=1
        )
        print("Created student user:")
        print(f"Username: student")
        print(f"Password: student123")
        print(f"Role: {student_user.role}")
        
except Exception as e:
    print(f"Error creating student user: {e}") 