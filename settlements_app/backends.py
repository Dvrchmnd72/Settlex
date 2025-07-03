import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

# ✅ Get the user model (supports custom user models)
User = get_user_model()

# ✅ Set up logger
logger = logging.getLogger(__name__)

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username:
            username = username.strip().lower()  # ✅ Remove extra spaces & normalize case

        user = None

        try:
            # ✅ Attempt login using email first
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            try:
                # ✅ If not found, try username (but only if different from email)
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                logger.warning(f"Authentication failed: No user found for {username}")
                return None

        if user and user.check_password(password):
            if not user.is_active:
                logger.warning(f"Authentication failed: User {username} is inactive")
                return None  # ✅ Prevent login if user is inactive
            return user
        else:
            logger.warning(f"Authentication failed: Invalid password for {username}")
            return None  # ✅ Prevent login if password is incorrect