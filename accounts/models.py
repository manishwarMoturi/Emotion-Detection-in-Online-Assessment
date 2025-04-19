from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class User(AbstractUser):
    STUDENT = 'student'
    TEST_TAKER = 'test_taker'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TEST_TAKER, 'Test Taker'),
        (ADMIN, 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT, db_index=True)
    institution = models.CharField(max_length=100, blank=True)
    student_id = models.CharField(max_length=50, blank=True, db_index=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['student_id']),
        ]
        
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
        
    def clean(self):
        if self.role == self.STUDENT and not self.student_id:
            raise ValidationError({'student_id': 'Student ID is required for students.'})
        if self.role == self.STUDENT and not self.institution:
            raise ValidationError({'institution': 'Institution is required for students.'})
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    @property
    def is_student(self):
        return self.role == self.STUDENT
        
    @property
    def is_test_taker(self):
        return self.role == self.TEST_TAKER
        
    @property
    def is_admin_user(self):
        return self.role == self.ADMIN 