import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emotion_detection.settings')
django.setup()

# Import models
from emotion_app.models import User

# Create an admin user
try:
    # Check if user already exists
    if User.objects.filter(username='admin').exists():
        print("Admin user already exists.")
        admin_user = User.objects.get(username='admin')
        admin_user.set_password('admin123')  # Reset password
        admin_user.save()
        print("Password reset to 'admin123'")
    else:
        # Create a new admin user
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True  # Allow access to Django admin
        )
        print("Created admin user:")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"Role: {admin_user.role}")
        
except Exception as e:
    print(f"Error creating admin user: {e}") 