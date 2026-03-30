from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Read-only representation of a user."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "is_active",
            "created_at",
            "date_joined",
        ]
        read_only_fields = ["id", "created_at", "date_joined"]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer used by admins to register new users."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def validate_password(self, value: str) -> str:
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Credentials for session-based login."""

    username = serializers.CharField()
    password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    """Allows an authenticated user to change their own password."""

    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate_new_password(self, value: str) -> str:
        if len(value) < 8:
            raise serializers.ValidationError(
                "New password must be at least 8 characters long."
            )
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admins to update user attributes."""

    class Meta:
        model = User
        fields = ["email", "role", "is_active"]
