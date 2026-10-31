from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import User
from accounts.services import validate_password, signup

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        # Normalize email to lowercase for case-insensitive login
        if 'email' in attrs:
            attrs['email'] = attrs['email'].lower()
        elif self.username_field in attrs:
            attrs[self.username_field] = attrs[self.username_field].lower()

        data = super().validate(attrs)
        # Contract with Anjali: return { access, refresh, role, name }
        data['role'] = self.user.role
        data['name'] = self.user.name or ''
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['name'] = user.name or ''
        token['email'] = user.email
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'role', 'date_joined']


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return signup(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', '')
        )


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)


class StaffCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_password(self, value):
        validate_password(value)
        return value


