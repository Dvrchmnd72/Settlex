from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser, User
from django_otp.plugins.otp_totp.models import TOTPDevice

from .views import send_message


class SendMessageTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.sender = User.objects.create_user(username='sender', password='pass')
        self.recipient = User.objects.create_user(username='recipient', password='pass')
        self.url = reverse('settlements_app:send_message')

    def _post(self, user, data):
        request = self.factory.post(self.url, data)
        request.user = user
        return send_message.__wrapped__.__wrapped__(request)

    def test_unauthenticated_request_returns_403(self):
        response = self._post(AnonymousUser(), {'message': 'hi', 'recipient': self.recipient.id})
        self.assertEqual(response.status_code, 403)

    def test_invalid_recipient_returns_404(self):
        response = self._post(self.sender, {'message': 'hi', 'recipient': 9999})
        self.assertEqual(response.status_code, 404)
