import logging

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .permissions import IsAdmin
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

User = get_user_model()
logger = logging.getLogger('accounts')


def _log_action(actor, action: str, object_type: str, object_id, metadata=None):
    """Safely delegate to the audit app's helper.

    If the audit app is not installed yet the call is silently skipped so
    that the accounts app can function independently during early
    development.
    """
    try:
        from audit.utils import log_action  # noqa: WPS433

        log_action(
            actor=actor,
            action=action,
            object_type=object_type,
            object_id=object_id,
            metadata=metadata,
        )
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# Authentication views
# ---------------------------------------------------------------------------


class LoginView(APIView):
    """Authenticate a user and start a session."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]

        user = authenticate(
            request,
            username=username,
            password=serializer.validated_data["password"],
        )

        if user is None:
            logger.warning(
                "Failed login attempt for username: %s", username
            )
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            # Return same message as invalid credentials to prevent
            # account enumeration
            logger.warning(
                "Login attempt on disabled account: %s", username
            )
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)

        _log_action(
            actor=user,
            action="login",
            object_type="user",
            object_id=user.pk,
        )

        return Response(
            {
                "user": UserSerializer(user).data,
                "csrf_token": get_token(request),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """End the current user session."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        _log_action(
            actor=request.user,
            action="logout",
            object_type="user",
            object_id=request.user.pk,
        )

        logout(request)

        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Registration (admin-only)
# ---------------------------------------------------------------------------


class RegisterView(APIView):
    """Create a new user account. Restricted to admins."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request: Request) -> Response:
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        _log_action(
            actor=request.user,
            action="register_user",
            object_type="user",
            object_id=user.pk,
            metadata={"username": user.username, "role": user.role},
        )

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Current user
# ---------------------------------------------------------------------------


class MeView(APIView):
    """Return the profile of the currently authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)


# ---------------------------------------------------------------------------
# User management (admin-only)
# ---------------------------------------------------------------------------


class UserListView(generics.ListAPIView):
    """List all users with pagination and filtering. Admin-only."""

    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "email"]
    ordering_fields = ["username", "date_joined", "role"]
    ordering = ["-date_joined"]


class UserDetailView(APIView):
    """Retrieve or partially update a user. Admin-only."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self, pk: int) -> User:
        return get_object_or_404(User, pk=pk)

    def get(self, request: Request, pk: int) -> Response:
        user = self.get_object(pk)
        return Response(UserSerializer(user).data)

    def patch(self, request: Request, pk: int) -> Response:
        user = self.get_object(pk)

        # Prevent admin from deactivating themselves
        if user.pk == request.user.pk and 'is_active' in request.data:
            if not request.data['is_active']:
                return Response(
                    {"detail": "You cannot deactivate your own account."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        _log_action(
            actor=request.user,
            action="update_user",
            object_type="user",
            object_id=user.pk,
            metadata={"changed_fields": list(request.data.keys())},
        )

        return Response(UserSerializer(user).data)


# ---------------------------------------------------------------------------
# Password management
# ---------------------------------------------------------------------------


class ChangePasswordView(APIView):
    """Allow an authenticated user to change their own password."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request, 'user': request.user},
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": ["Current password is incorrect."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        update_session_auth_hash(request, user)

        _log_action(
            actor=user,
            action="change_password",
            object_type="user",
            object_id=user.pk,
        )

        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )
