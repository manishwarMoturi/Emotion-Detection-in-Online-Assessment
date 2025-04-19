from django.db import models
from django.conf import settings
from exams.models import StudentExam, Question

class EmotionRecord(models.Model):
    EMOTION_CHOICES = [
        ('focused', 'Focused'),
        ('confused', 'Confused'),
        ('stressed', 'Stressed'),
        ('confident', 'Confident'),
        ('neutral', 'Neutral'),
    ]
    
    student_exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE, related_name='emotion_records')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='emotion_records', null=True, blank=True)
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'emotion_records'
        ordering = ['student_exam', 'timestamp']
    
    def __str__(self):
        return f"{self.student_exam.student.username} - {self.emotion} at {self.timestamp}"

class EmotionSummary(models.Model):
    student_exam = models.OneToOneField(StudentExam, on_delete=models.CASCADE, related_name='emotion_summary')
    focus_level = models.DecimalField(max_digits=5, decimal_places=2)
    stress_level = models.DecimalField(max_digits=5, decimal_places=2)
    confusion_level = models.DecimalField(max_digits=5, decimal_places=2)
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'emotion_summaries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Emotion Summary - {self.student_exam.student.username} - {self.student_exam.exam.title}"

class EmotionFeedback(models.Model):
    student_exam = models.OneToOneField(StudentExam, on_delete=models.CASCADE, related_name='emotion_feedback')
    feedback = models.TextField()
    recommendations = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'emotion_feedback'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Emotion Feedback - {self.student_exam.student.username} - {self.student_exam.exam.title}" 