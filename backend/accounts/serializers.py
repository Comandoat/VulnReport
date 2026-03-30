from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
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

    password = serializers.CharField(write_only=True, min_length=12)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def validate_password(self, value: str) -> str:
        validate_password(value)
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
    new_password = serializers.CharField(min_length=12)

    def validate_new_password(self, value: str) -> str:
        validate_password(value, user=self.context.get('user'))
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admins to update user attributes."""

    class Meta:
        model = User
        fields = ["email", "role", "is_active"]

    def validate(self, attrs):
        request = self.context.get('request')
        if request and self.instance:
            # Prevent admin from demoting themselves
            if self.instance.pk == request.user.pk:
                if 'role' in attrs and attrs['role'] != self.instance.role:
                    raise serializers.ValidationError(
                        {"role": "You cannot change your own role."}
                    )
                if 'is_active' in attrs and not attrs['is_active']:
                    raise serializers.ValidationError(
                        {"is_active": "You cannot deactivate your own account."}
                    )
        return attrs
