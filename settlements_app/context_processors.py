from .models import Instruction
from datetime import datetime
from django.contrib.auth.models import User


def chat_visibility(request):
    """
    Controls whether the chat widget should be shown based on the current path.
    """
    path = request.path

    excluded_prefixes = [
        "/login/",
        "/account/login/",
        "/account/two_factor/",
        "/two_factor/",
        "/password-reset/",
        "/reset/",
        "/admin/",
    ]

    show_chat = request.user.is_authenticated and not any(path.startswith(prefix) for prefix in excluded_prefixes)

    return {
        "enable_chat": show_chat
    }


def latest_instruction(request):
    """
    Adds the user's latest instruction to the template context.
    """
    if request.user.is_authenticated:
        try:
            solicitor = request.user.solicitor  # This assumes a OneToOne link: Solicitor.user
            latest = Instruction.objects.filter(solicitor=solicitor).last()
        except Exception:
            latest = None

        return {
            'latest_instruction': latest
        }
    return {}

def static_version(request):
    return {'STATIC_VERSION': int(datetime.now().timestamp())}


def admin_user(request):
    """Provide the primary admin user's ID for chat functionality."""
    try:
        admin = User.objects.filter(is_superuser=True).first()
        return {"admin_user_id": admin.id if admin else None}
    except Exception:
        return {"admin_user_id": None}