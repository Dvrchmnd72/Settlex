from django.test import TestCase, RequestFactory, Client, override_settings
from datetime import date
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser, User
from unittest.mock import patch
from django.contrib.messages.storage.fallback import FallbackStorage
from docx import Document
import io


from .views import (
    send_message,
    settlement_calculator,
    settlement_statement,
    settlement_statement_word,
    payment_direction,
)
from .models import Firm, Solicitor, Instruction, PaymentDirection

class SendMessageTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.sender = User.objects.create_user(username='sender', password='pass')
        self.recipient = User.objects.create_user(username='recipient', password='pass')
        self.url = reverse('settlements_app:send_message')

    def _post(self, user, data):
        request = self.factory.post(self.url, data)
        request.user = user
        # Bypass the @login_required decorator for direct view call
        with patch('django.contrib.auth.decorators.login_required', lambda x: x):
            return send_message(request)  # Call the view directly

    def test_unauthenticated_request_returns_403(self):
        response = self.client.post(self.url, {'message': 'hi', 'recipient': self.recipient.id})
        self.assertEqual(response.status_code, 403)

    def test_invalid_recipient_returns_404(self):
        response = self._post(self.sender, {'message': 'hi', 'recipient': 9999})
        self.assertEqual(response.status_code, 404)


@override_settings(DEBUG=False)
class SettlementCalculatorTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_blank_deposit_and_release_fee(self):
        url = reverse('settlements_app:settlement_calculator')
        data = {
            'settlement_date': '2023-01-01',
            'adjustment_date': '2023-01-01',
            'contract_date': '2023-01-01',
            'deposit': '',
            'release_mortgage_fee': '',
        }
        request = self.factory.post(url, data)
        request.session = self.client.session
        request.user = AnonymousUser()

        response = settlement_calculator(request)
        self.assertEqual(response.status_code, 302)

        request.session.save()

        request = self.factory.get(reverse('settlements_app:settlement_statement'))
        request.session = self.client.session
        request.user = AnonymousUser()

        response = settlement_statement(request)
        self.assertEqual(response.status_code, 200)

        session_data = request.session.get('settlement_data')
        self.assertEqual(session_data['deposit'], 0)
        self.assertEqual(session_data['release_mortgage_fee'], 0)


class PaymentDirectionViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(username='pdir_user', password='pass')
        self.firm = Firm.objects.create(name='Firm', contact_email='f@example.com')
        self.solicitor = Solicitor.objects.create(
            user=self.user,
            instructing_solicitor='Tester',
            firm=self.firm,
        )
        self.instruction = Instruction.objects.create(
            solicitor=self.solicitor,
            file_reference='REF123',
            settlement_type='purchase',
            settlement_date=date.today(),
            title_reference='TR1',
        )
        self.url = reverse('settlements_app:payment_direction', args=[self.instruction.id])

    def _call_view(self, method='get', data=None):
        if method == 'post':
            request = self.factory.post(self.url, data or {})
        else:
            request = self.factory.get(self.url)
        request.user = self.user
        request.session = self.client.session
        setattr(request, '_messages', FallbackStorage(request))
        with patch('django.contrib.auth.decorators.login_required', lambda x: x):
            return payment_direction(request, instruction_id=self.instruction.id)

    def test_get_displays_form(self):
        response = self._call_view('get')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment Directions')

    def test_post_creates_payment_direction_and_redirects(self):
        data = {'registration_fee': '10.00', 'pexa_fee': '20.00'}
        response = self._call_view('post', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('settlements_app:view_transaction', args=[self.instruction.id])
        )
        pd = PaymentDirection.objects.get(instruction=self.instruction)
        self.assertEqual(pd.registration_fee, Decimal('10.00'))
        self.assertEqual(pd.pexa_fee, Decimal('20.00'))


class SettlementStatementWordTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_word_generation_returns_200(self):
        url = reverse('settlements_app:settlement_statement_word')
        session = self.client.session
        session['settlement_data'] = {
            'contract_price': '1000',
            'deposit': '100',
        }
        session.save()

        request = self.factory.get(url)
        request.session = self.client.session
        request.user = AnonymousUser()
        response = settlement_statement_word(request)
        self.assertEqual(response.status_code, 200)

        content = b"".join(response.streaming_content)
        doc = Document(io.BytesIO(content))
        text = "\n".join(p.text for p in doc.paragraphs)
        self.assertIn("Settlement Statement", text)

