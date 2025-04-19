from django.urls import path
from .views import (
    EmotionRecordCreateView, EmotionRecordListView,
    GenerateEmotionSummaryView, EmotionSummaryView,
    GenerateEmotionFeedbackView, EmotionFeedbackView
)

urlpatterns = [
    # Emotion records
    path('record/', EmotionRecordCreateView.as_view(), name='emotion-record-create'),
    path('records/<int:student_exam_id>/', EmotionRecordListView.as_view(), name='emotion-record-list'),
    
    # Emotion summaries
    path('summary/<int:student_exam_id>/', EmotionSummaryView.as_view(), name='emotion-summary'),
    path('summary/<int:student_exam_id>/generate/', GenerateEmotionSummaryView.as_view(), name='generate-emotion-summary'),
    
    # Emotion feedback
    path('feedback/<int:student_exam_id>/', EmotionFeedbackView.as_view(), name='emotion-feedback'),
    path('feedback/<int:student_exam_id>/generate/', GenerateEmotionFeedbackView.as_view(), name='generate-emotion-feedback'),
] 