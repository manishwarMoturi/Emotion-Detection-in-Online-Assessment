import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emotion_detection.settings')
django.setup()

# Import models
from emotion_app.models import User

# Create a test-taker user
try:
    # Check if user already exists
    if User.objects.filter(username='testtaker').exists():
        print("Testtaker user already exists.")
        test_taker = User.objects.get(username='testtaker')
        test_taker.set_password('testtaker123')  # Reset password
        test_taker.save()
        print("Password reset to 'testtaker123'")
    else:
        # Create a new test-taker user
        test_taker = User.objects.create_user(
            username='testtaker',
            email='testtaker@example.com',
            password='testtaker123',
            first_name='Test',
            last_name='Taker',
            role='testtaker'
        )
        print("Created test-taker user:")
        print(f"Username: testtaker")
        print(f"Password: testtaker123")
        print(f"Role: {test_taker.role}")
        
except Exception as e:
    print(f"Error creating test-taker user: {e}") 