from rest_framework import serializers
from .models import EmotionRecord, EmotionSummary, EmotionFeedback

class EmotionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionRecord
        fields = '__all__'
        read_only_fields = ('timestamp',)

class EmotionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionSummary
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class EmotionFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionFeedback
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class EmotionRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionRecord
        fields = ('student_exam', 'question', 'emotion', 'confidence_score')
        
    def validate(self, attrs):
        student_exam = attrs['student_exam']
        if student_exam.status != 'in_progress':
            raise serializers.ValidationError("Cannot record emotions for an exam that is not in progress.")
        return attrs

class EmotionSummaryDetailSerializer(serializers.ModelSerializer):
    student_exam = serializers.SerializerMethodField()
    
    class Meta:
        model = EmotionSummary
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        
    def get_student_exam(self, obj):
        return {
            'id': obj.student_exam.id,
            'student': {
                'id': obj.student_exam.student.id,
                'username': obj.student_exam.student.username,
                'full_name': f"{obj.student_exam.student.first_name} {obj.student_exam.student.last_name}"
            },
            'exam': {
                'id': obj.student_exam.exam.id,
                'title': obj.student_exam.exam.title
            }
        }

class EmotionFeedbackDetailSerializer(serializers.ModelSerializer):
    student_exam = serializers.SerializerMethodField()
    emotion_summary = EmotionSummarySerializer(read_only=True)
    
    class Meta:
        model = EmotionFeedback
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        
    def get_student_exam(self, obj):
        return {
            'id': obj.student_exam.id,
            'student': {
                'id': obj.student_exam.student.id,
                'username': obj.student_exam.student.username,
                'full_name': f"{obj.student_exam.student.first_name} {obj.student_exam.student.last_name}"
            },
            'exam': {
                'id': obj.student_exam.exam.id,
                'title': obj.student_exam.exam.title
            }
        } 