from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import (
    home, logout_view, register, new_instruction, upload_documents,
    my_transactions, solicitor_dashboard, edit_instruction, delete_instruction,
    payment_direction, view_transaction, long_poll_messages, check_new_messages,
    send_message, reply_view, mark_messages_read, check_typing_status,
    upload_chat_file, delete_message, settlement_calculator, settlement_statement,
    settlement_statement_word, list_payment_directions, delete_line_item,
    edit_line_item, rates_adjustment_view,
)
from settlements_app.views import SettlexTwoFactorSetupView
from two_factor.views import LoginView

app_name = 'settlements_app'

urlpatterns = [
    # Public views
    path("", home, name="home"),
    path("login/", LoginView.as_view(), name="login"),
    path("account/two_factor/setup/", SettlexTwoFactorSetupView.as_view(), name="two_factor_setup"),
    path("logout/", logout_view, name="logout"),
    path("register/", register, name="register"),

    # Instruction management
    path("new-instruction/", new_instruction, name="new_instruction"),
    path("upload-documents/", upload_documents, name="upload_documents"),
    path("my-transactions/", my_transactions, name="my_transactions"),
    path("dashboard/", solicitor_dashboard, name="solicitor_dashboard"),
    path("edit-instruction/<int:id>/", edit_instruction, name="edit_instruction"),
    path("delete-instruction/<int:id>/", delete_instruction, name="delete_instruction"),

    # Payment Directions
    path("payment-direction/<int:instruction_id>/", payment_direction, name="payment_direction"),
    path("payment-directions/", list_payment_directions, name="list_payment_directions"),
    path("delete-line-item/<int:item_id>/", delete_line_item, name="delete_line_item"),
    path("edit-line-item/", edit_line_item, name="edit_line_item"),

    # Transaction and Settlement
    path("transaction/<int:transaction_id>/", view_transaction, name="view_transaction"),
    path("settlement-calculator/", settlement_calculator, name="settlement_calculator"),
    path("settlement-statement/", settlement_statement, name="settlement_statement"),
    path("settlement-statement-word/", settlement_statement_word, name="settlement_statement_word"),

    # Adjustments
    path('adjustments/rates/<int:instruction_id>/', rates_adjustment_view, name='rates_adjustment'),




    # Chat functionality
    path("long-poll-messages/", long_poll_messages, name="long_poll_messages"),
    path("check-new-messages/", check_new_messages, name="check_new_messages"),
    path("send-message/", send_message, name="send_message"),
    path("reply/<int:message_id>/", reply_view, name="reply_view"),
    path("mark-messages-read/", mark_messages_read, name="mark_messages_read"),
    path("check-typing-status/", check_typing_status, name="check_typing_status"),
    path("upload-file/", upload_chat_file, name="upload_chat_file"),
    path("delete-message/", delete_message, name="delete_message"),

    # Password Reset Flow
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="settlements_app/password_reset.html",
        success_url=reverse_lazy("settlements_app:password_reset_done"),
        email_template_name="settlements_app/password_reset_email.html",
        subject_template_name="settlements_app/password_reset_subject.txt"
    ), name="password_reset"),

    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="settlements_app/password_reset_done.html"
    ), name="password_reset_done"),

    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="settlements_app/password_reset_confirm.html",
        success_url=reverse_lazy("settlements_app:password_reset_complete")
    ), name="password_reset_confirm"),

    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="settlements_app/password_reset_complete.html"
    ), name="password_reset_complete"),
]