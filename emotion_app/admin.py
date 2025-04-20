from django.contrib import admin
from .models import User, Question, ExamAttempt

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text_preview', 'difficulty_level', 'category', 'created_at')
    list_filter = ('difficulty_level', 'category', 'created_at')
    search_fields = ('question_text', 'category')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def question_text_preview(self, obj):
        """Return a truncated version of the question text"""
        if len(obj.question_text) > 50:
            return obj.question_text[:50] + "..."
        return obj.question_text
    
    question_text_preview.short_description = 'Question Text'
    
    # Custom JSON display for test cases
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['test_cases_json'].help_text = 'JSON format for test cases. Edit with caution.'
        return form

class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'start_time', 'end_time', 'score', 'most_frequent_emotion')
    list_filter = ('start_time', 'end_time', 'most_frequent_emotion')
    search_fields = ('user__username', 'exam_id')
    readonly_fields = ('id', 'start_time')
    
    # Customize display for JSON fields
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'exam_id', 'start_time', 'end_time', 'score', 'most_frequent_emotion')
        }),
        ('Advanced Details', {
            'classes': ('collapse',),
            'fields': ('questions_json', 'logged_emotions_json', 'submissions_json'),
        }),
    )

# Register models
admin.site.register(Question, QuestionAdmin)
admin.site.register(ExamAttempt, ExamAttemptAdmin)

# User model is already registered via Django's user admin
