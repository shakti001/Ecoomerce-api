from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

# Get the user model defined in the Django project (can be custom)
User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend to allow login with email instead of username.
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            # Try to get the user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # If no user is found with the given email, return None
            return None

        # Check if the password is correct and user is allowed to authenticate
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        # If password is incorrect or not allowed to authenticate, return None
        return None

