from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'email', 'first_name', 'last_name',
                 'role', 'institution', 'student_id', 'phone', 'profile_picture')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data.get('role', User.STUDENT),
            institution=validated_data.get('institution', ''),
            student_id=validated_data.get('student_id', ''),
            phone=validated_data.get('phone', '')
        )
        user.set_password(validated_data['password'])
        
        if 'profile_picture' in validated_data:
            user.profile_picture = validated_data['profile_picture']
            
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'institution', 'student_id', 'phone', 'profile_picture')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False}
        }

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs 