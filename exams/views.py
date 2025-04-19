from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Exam, Question, StudentExam, Submission
from .serializers import (
    ExamSerializer, ExamDetailSerializer, QuestionSerializer,
    StudentExamSerializer, StudentExamDetailSerializer,
    SubmissionSerializer, SubmissionDetailSerializer
)
from accounts.permissions import IsAdminUser, IsTestTakerOrAdmin, IsStudent

class ExamListCreateView(generics.ListCreateAPIView):
    serializer_class = ExamSerializer
    permission_classes = (IsTestTakerOrAdmin,)
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Exam.objects.all()
        return Exam.objects.filter(created_by=self.request.user)

class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    permission_classes = (IsTestTakerOrAdmin,)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ExamDetailSerializer
        return ExamSerializer

class QuestionListCreateView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (IsTestTakerOrAdmin,)
    
    def get_queryset(self):
        exam_id = self.kwargs['exam_id']
        return Question.objects.filter(exam_id=exam_id)
    
    def perform_create(self, serializer):
        exam = get_object_or_404(Exam, id=self.kwargs['exam_id'])
        serializer.save(exam=exam)

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (IsTestTakerOrAdmin,)

class StudentExamListView(generics.ListAPIView):
    serializer_class = StudentExamSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        if self.request.user.role == 'student':
            return StudentExam.objects.filter(student=self.request.user)
        return StudentExam.objects.all()

class StudentExamDetailView(generics.RetrieveAPIView):
    serializer_class = StudentExamDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        if self.request.user.role == 'student':
            return StudentExam.objects.filter(student=self.request.user)
        return StudentExam.objects.all()

class StartExamView(APIView):
    permission_classes = (IsStudent,)
    
    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        
        # Check if exam can be started
        if timezone.now() < exam.start_time:
            return Response(
                {"error": "Exam has not started yet"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if timezone.now() > exam.end_time:
            return Response(
                {"error": "Exam has ended"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create student exam
        student_exam, created = StudentExam.objects.get_or_create(
            student=request.user,
            exam=exam,
            defaults={'status': 'in_progress', 'start_time': timezone.now()}
        )
        
        if not created and student_exam.status == 'completed':
            return Response(
                {"error": "You have already completed this exam"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = StudentExamDetailSerializer(student_exam)
        return Response(serializer.data)

class SubmitAnswerView(APIView):
    permission_classes = (IsStudent,)
    
    def post(self, request, exam_id, question_id):
        student_exam = get_object_or_404(
            StudentExam,
            exam_id=exam_id,
            student=request.user,
            status='in_progress'
        )
        
        question = get_object_or_404(Question, id=question_id, exam_id=exam_id)
        
        serializer = SubmissionSerializer(data={
            'student_exam': student_exam.id,
            'question': question.id,
            'code': request.data.get('code'),
            'language': request.data.get('language')
        })
        
        if serializer.is_valid():
            submission = serializer.save()
            # Here you would typically run the code against test cases
            # and update the submission score and feedback
            return Response(SubmissionDetailSerializer(submission).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FinishExamView(APIView):
    permission_classes = (IsStudent,)
    
    def post(self, request, pk):
        student_exam = get_object_or_404(
            StudentExam,
            exam_id=pk,
            student=request.user,
            status='in_progress'
        )
        
        student_exam.status = 'completed'
        student_exam.end_time = timezone.now()
        
        # Calculate final score
        submissions = student_exam.submissions.all()
        total_points = sum(sub.question.points for sub in submissions)
        earned_points = sum(sub.score or 0 for sub in submissions)
        student_exam.score = (earned_points / total_points * 100) if total_points > 0 else 0
        
        student_exam.save()
        
        return Response(StudentExamDetailSerializer(student_exam).data) 