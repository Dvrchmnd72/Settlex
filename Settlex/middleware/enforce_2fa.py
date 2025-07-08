import logging
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from two_factor.utils import default_device

logger = logging.getLogger(__name__)

class Enforce2FAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # ✅ Exempt: Admin, 2FA, static/media
        exempt_paths = (
            path.startswith('/admin/') or
            path.startswith('/account/') or
            path.startswith('/two_factor/') or
            path.startswith('/static/') or
            path.startswith('/media/')
        )

        if exempt_paths:
            return self.get_response(request)

        # ✅ Enforce 2FA for authenticated, non-staff users only
        if request.user.is_authenticated and not request.user.is_staff:
            if not default_device(request.user):
                try:
                    safe_paths = [
                        reverse('settlements_app:login'),
                        reverse('settlements_app:logout'),
                        reverse('settlements_app:two_factor_setup'),
                    ]
                except NoReverseMatch:
                    logger.warning("❌ Reverse match failed for 2FA-safe paths.")
                    safe_paths = []

                if not any(path.startswith(p) for p in safe_paths):
                    logger.debug("🔒 2FA not set — redirecting user %s to setup", request.user)
                    return redirect('settlements_app:two_factor_setup')

        return self.get_response(request)
