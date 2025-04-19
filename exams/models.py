from django.db import models
from django.conf import settings

class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_minutes = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    passing_score = models.DecimalField(max_digits=5, decimal_places=2)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exams'
        ordering = ['-start_time']
    
    def __str__(self):
        return self.title

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    test_cases = models.JSONField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['exam', 'id']
    
    def __str__(self):
        return f"{self.exam.title} - {self.title}"

class StudentExam(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_exams')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='student_exams')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_exams'
        unique_together = ['student', 'exam']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"

class Submission(models.Model):
    student_exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE, related_name='submissions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    language = models.CharField(max_length=20)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'submissions'
        unique_together = ['student_exam', 'question']
        ordering = ['question']
    
    def __str__(self):
        return f"{self.student_exam.student.username} - {self.question.title}" 