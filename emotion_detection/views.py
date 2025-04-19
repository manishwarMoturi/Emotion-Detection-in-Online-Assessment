from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import EmotionRecord, EmotionSummary, EmotionFeedback
from .serializers import (
    EmotionRecordSerializer, EmotionRecordCreateSerializer,
    EmotionSummarySerializer, EmotionSummaryDetailSerializer,
    EmotionFeedbackSerializer, EmotionFeedbackDetailSerializer
)
from exams.models import StudentExam
from accounts.permissions import IsTestTakerOrAdmin

class EmotionRecordCreateView(generics.CreateAPIView):
    serializer_class = EmotionRecordCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def perform_create(self, serializer):
        student_exam = serializer.validated_data['student_exam']
        if student_exam.student != self.request.user:
            raise permissions.PermissionDenied("You can only record emotions for your own exams.")
        serializer.save()

class EmotionRecordListView(generics.ListAPIView):
    serializer_class = EmotionRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        student_exam_id = self.kwargs['student_exam_id']
        student_exam = get_object_or_404(StudentExam, id=student_exam_id)
        
        if student_exam.student != self.request.user and not (
            self.request.user.role in ['test_taker', 'admin']
        ):
            raise permissions.PermissionDenied(
                "You can only view emotion records for your own exams."
            )
            
        return EmotionRecord.objects.filter(student_exam_id=student_exam_id)

class GenerateEmotionSummaryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request, student_exam_id):
        student_exam = get_object_or_404(StudentExam, id=student_exam_id)
        
        if student_exam.student != request.user and not (
            request.user.role in ['test_taker', 'admin']
        ):
            raise permissions.PermissionDenied(
                "You can only generate summaries for your own exams."
            )
        
        # Calculate emotion levels
        emotion_records = EmotionRecord.objects.filter(student_exam=student_exam)
        
        focus_records = emotion_records.filter(emotion='focused')
        stress_records = emotion_records.filter(emotion='stressed')
        confusion_records = emotion_records.filter(emotion='confused')
        confidence_records = emotion_records.filter(emotion='confident')
        
        summary, created = EmotionSummary.objects.update_or_create(
            student_exam=student_exam,
            defaults={
                'focus_level': focus_records.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0,
                'stress_level': stress_records.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0,
                'confusion_level': confusion_records.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0,
                'confidence_level': confidence_records.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0
            }
        )
        
        return Response(EmotionSummaryDetailSerializer(summary).data)

class EmotionSummaryView(generics.RetrieveAPIView):
    serializer_class = EmotionSummaryDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        student_exam_id = self.kwargs['student_exam_id']
        student_exam = get_object_or_404(StudentExam, id=student_exam_id)
        
        if student_exam.student != self.request.user and not (
            self.request.user.role in ['test_taker', 'admin']
        ):
            raise permissions.PermissionDenied(
                "You can only view emotion summaries for your own exams."
            )
            
        return get_object_or_404(EmotionSummary, student_exam_id=student_exam_id)

class GenerateEmotionFeedbackView(APIView):
    permission_classes = (IsTestTakerOrAdmin,)
    
    def post(self, request, student_exam_id):
        student_exam = get_object_or_404(StudentExam, id=student_exam_id)
        emotion_summary = get_object_or_404(EmotionSummary, student_exam=student_exam)
        
        # Generate feedback based on emotion summary
        feedback = "Based on your emotion analysis during the exam:\n\n"
        
        if emotion_summary.focus_level >= 0.7:
            feedback += "- You maintained excellent focus throughout the exam.\n"
        elif emotion_summary.focus_level >= 0.5:
            feedback += "- Your focus was moderate but could be improved.\n"
        else:
            feedback += "- You struggled to maintain focus during the exam.\n"
            
        if emotion_summary.stress_level >= 0.7:
            feedback += "- You experienced high levels of stress.\n"
            recommendations = (
                "Consider practicing stress management techniques like deep breathing "
                "before and during exams."
            )
        else:
            feedback += "- You managed stress well during the exam.\n"
            recommendations = "Keep up your good stress management practices."
            
        if emotion_summary.confusion_level >= 0.6:
            feedback += "- You showed signs of confusion with some questions.\n"
            recommendations += (
                "\nReview the topics that caused confusion and consider seeking "
                "additional help in those areas."
            )
            
        emotion_feedback, created = EmotionFeedback.objects.update_or_create(
            student_exam=student_exam,
            defaults={
                'feedback': feedback,
                'recommendations': recommendations
            }
        )
        
        return Response(EmotionFeedbackDetailSerializer(emotion_feedback).data)

class EmotionFeedbackView(generics.RetrieveAPIView):
    serializer_class = EmotionFeedbackDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        student_exam_id = self.kwargs['student_exam_id']
        student_exam = get_object_or_404(StudentExam, id=student_exam_id)
        
        if student_exam.student != self.request.user and not (
            self.request.user.role in ['test_taker', 'admin']
        ):
            raise permissions.PermissionDenied(
                "You can only view emotion feedback for your own exams."
            )
            
        return get_object_or_404(EmotionFeedback, student_exam_id=student_exam_id) 