from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

# Custom serializer to authenticate a user using email and password,
# and return JWT tokens (access and refresh)
class EmailTokenObtainPairSerializer(serializers.Serializer):
    # Email field for user login
    email = serializers.EmailField()

    # Password field (write-only for security)
    password = serializers.CharField(write_only=True)

    # Custom validation method to authenticate user and return tokens
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Ensure both email and password are provided
        if email and password:
            # Attempt to authenticate user using email and password
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            # If authentication fails, raise error
            if not user:
                raise serializers.ValidationError(
                    _("Invalid email or password"), code='authorization'
                )
        else:
            # If either email or password is missing, raise error
            raise serializers.ValidationError(
                _("Must include email and password"), code='authorization'
            )

        # If user is authenticated, generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Return both tokens and user information
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'email': user.email,
        }
