from django.contrib import admin
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Solicitor, Instruction, Document, Firm, ChatMessage
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@admin.register(Firm)
class FirmAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "contact_number", "state")
    search_fields = ("name", "contact_email", "contact_number")
    list_filter = ("state",)

@admin.register(Solicitor)
class SolicitorAdmin(admin.ModelAdmin):
    list_display = ("instructing_solicitor", "get_firm_name", "office_phone", "mobile_phone", "profession")
    search_fields = ("instructing_solicitor", "firm__name")
    list_filter = ("firm",)

    def get_firm_name(self, obj):
        return obj.firm.name if obj.firm else "No Firm Assigned"
    get_firm_name.short_description = "Firm Name"

@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = (
        "file_reference", "settlement_type", "solicitor",
        "purchaser_name", "purchaser_email", "purchaser_mobile",
        "purchaser_address", "seller_name", "seller_address",
        "full_transaction_address", "property_type",
        "title_reference", "settlement_date", "status", "date_created"
    )
    search_fields = (
        "file_reference", "solicitor__user__email",
        "purchaser_name", "seller_name",
        "transaction_street_address", "transaction_suburb", "transaction_state", "transaction_postcode",
        "title_reference"
    )
    list_filter = ("settlement_type", "status", "property_type", "date_created")
    list_editable = ("status",)
    ordering = ("-date_created",)

    def full_transaction_address(self, obj):
        parts = [
            obj.transaction_street_address or '',
            obj.transaction_suburb or '',
            obj.transaction_state or '',
            obj.transaction_postcode or ''
        ]
        return ", ".join(filter(None, parts))
    full_transaction_address.short_description = "Transaction Address"

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "instruction", "document_type", "uploaded_at")
    search_fields = ("name", "instruction__file_reference")
    list_filter = ("document_type", "uploaded_at")

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("sender_name", "recipient_name", "message_preview", "timestamp", "reply_button")
    search_fields = ("sender__username", "recipient__username", "message")
    list_filter = ("timestamp",)
    ordering = ("-timestamp",)
    readonly_fields = ('is_read',)

    def sender_name(self, obj):
        return "Settlex (Admin)" if obj.sender.is_superuser else (obj.sender.get_full_name() or obj.sender.username)
    sender_name.short_description = "Sender"

    def recipient_name(self, obj):
        return obj.recipient.get_full_name() or obj.recipient.username
    recipient_name.short_description = "Recipient"

    def message_preview(self, obj):
        return obj.message[:50] + "..." if obj.message and len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message Preview"

    def reply_button(self, obj):
        return format_html(
            '<a href="{}" class="chat-reply-button" '
            'style="display:inline-block; width:120px; padding:10px 15px; '
            'font-size:14px; text-align:center; background-color:#007bff; '
            'color:white; border:none; border-radius:6px; cursor:pointer; '
            'transition:0.3s ease-in-out; text-decoration:none;">Reply</a>',
            reverse("admin:chat_reply", args=[obj.id])
        )
    reply_button.short_description = "Reply"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('chatmessage/<int:message_id>/reply/', self.admin_site.admin_view(self.reply_view), name="chat_reply"),
        ]
        return custom_urls + urls

    @method_decorator(csrf_exempt)
    def reply_view(self, request, message_id):
        message = get_object_or_404(ChatMessage, id=message_id)
        if request.method == "POST":
            reply_text = request.POST.get("reply_message", "").strip()
            if reply_text:
                ChatMessage.objects.create(
                    sender=request.user,
                    recipient=message.sender,
                    message=reply_text
                )
                messages.success(request, "Reply sent successfully!")
                return HttpResponseRedirect(reverse("admin:settlements_app_chatmessage_changelist"))
        context = {
            "message": message,
            "subtitle": "Replying to Chat Message",
        }
        return render(request, "admin/chat_reply.html", context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        message = self.get_object(request, object_id)
        if message and not message.is_read and request.user.is_staff:
            message.is_read = True
            message.save()
        return super().change_view(request, object_id, form_url, extra_context)

    class Media:
        js = ('admin/js/jquery.init.js',)

def send_activation_email(modeladmin, request, queryset):
    for user in queryset:
        if not user.is_active:
            messages.warning(request, f"User {user.email} is not active.")
            continue
        subject = "Your SettleX Account Has Been Activated"
        message = f"""
        Dear {user.first_name} {user.last_name},

        Your account has been successfully activated. You can now log in to SettleX.

        Login here: https://settlex.onestoplegal.com.au

        Regards,
        SettleX Team
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(request, f"Activation email sent to {user.email}")
        except Exception as e:
            messages.error(request, f"Failed to send activation email to {user.email}: {e}")

send_activation_email.short_description = "✅ Send Activation Email"

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_active")
    list_filter = ("is_active",)
    actions = [send_activation_email]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
