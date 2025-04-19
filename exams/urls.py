from django.urls import path
from .views import (
    ExamListCreateView, ExamDetailView,
    QuestionListCreateView, QuestionDetailView,
    StudentExamListView, StudentExamDetailView,
    StartExamView, SubmitAnswerView, FinishExamView
)

urlpatterns = [
    # Exam management
    path('', ExamListCreateView.as_view(), name='exam-list'),
    path('<int:pk>/', ExamDetailView.as_view(), name='exam-detail'),
    
    # Question management
    path('<int:exam_id>/questions/', QuestionListCreateView.as_view(), name='question-list'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    
    # Student exam interactions
    path('student-exams/', StudentExamListView.as_view(), name='student-exam-list'),
    path('student-exams/<int:pk>/', StudentExamDetailView.as_view(), name='student-exam-detail'),
    path('<int:pk>/start/', StartExamView.as_view(), name='start-exam'),
    path('<int:exam_id>/submit/<int:question_id>/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('<int:pk>/finish/', FinishExamView.as_view(), name='finish-exam'),
] 