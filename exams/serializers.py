from rest_framework import serializers
from .models import Exam, Question, StudentExam, Submission
from django.contrib.auth import get_user_model

User = get_user_model()

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Exam
        fields = '__all__'
        
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ('score', 'feedback')

class StudentExamSerializer(serializers.ModelSerializer):
    submissions = SubmissionSerializer(many=True, read_only=True)
    exam = ExamSerializer(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = StudentExam
        fields = '__all__'
        read_only_fields = ('status', 'start_time', 'end_time', 'score')

class ExamDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = Exam
        fields = '__all__'
        
    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        exam = Exam.objects.create(**validated_data)
        
        for question_data in questions_data:
            Question.objects.create(exam=exam, **question_data)
            
        return exam
        
    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if questions_data is not None:
            instance.questions.all().delete()
            for question_data in questions_data:
                Question.objects.create(exam=instance, **question_data)
                
        return instance

class SubmissionDetailSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ('student_exam', 'score', 'feedback')

class StudentExamDetailSerializer(serializers.ModelSerializer):
    submissions = SubmissionDetailSerializer(many=True, read_only=True)
    exam = ExamSerializer(read_only=True)
    student = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentExam
        fields = '__all__'
        
    def get_student(self, obj):
        return {
            'id': obj.student.id,
            'username': obj.student.username,
            'full_name': f"{obj.student.first_name} {obj.student.last_name}",
            'email': obj.student.email
        } 