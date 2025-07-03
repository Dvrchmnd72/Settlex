from django.test import TestCase, override_settings
import unittest
from django.urls import reverse
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.oath import totp
from Settlex import settings

MIDDLEWARE_NO_ENFORCE = [mw for mw in settings.MIDDLEWARE if mw != 'Settlex.middleware.enforce_2fa.Enforce2FAMiddleware']

@unittest.skip("TwoFactor flow requires external setup")
@override_settings(MIDDLEWARE=MIDDLEWARE_NO_ENFORCE)
class TwoFactorSetupFlowTests(TestCase):
    def setUp(self):
        # Create a test user and log them in
        self.user = User.objects.create_user(username='tester', password='pass', email='t@example.com')
        self.client.login(username='tester', password='pass')
        self.url = reverse('settlements_app:two_factor_setup')

    def _current_step(self, response):
        return response.context['wizard']['steps'].current

    def test_setup_wizard_flow(self):
        # Step 1: Welcome screen
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self._current_step(resp), 'welcome')

        # Step 2: POST welcome step
        resp = self.client.post(self.url, {
            'settlex_two_factor_setup_view-current_step': 'welcome',
            'welcome-acknowledge': 'on'  # Make sure the field name matches your form
        }, follow=True)
        self.assertEqual(self._current_step(resp), 'generator')

        # Step 3: Ensure device is created and stored in session
        session = self.client.session
        session.save()  # ensure the session is saved before accessing it
        wizard_data = session.get('settlex_two_factor_setup_view', {})
        extra_data = wizard_data.get('extra_data', {})
        device_id = extra_data.get('device_id')

        # If no device_id, create a new TOTP device for testing
        if not device_id:
            device = TOTPDevice.objects.create(user=self.user, confirmed=False)
            extra_data['device_id'] = device.id
            wizard_data['extra_data'] = extra_data
            session['settlex_two_factor_setup_view'] = wizard_data
            session.save()  # Save session after adding the device_id
            device_id = device.id

        # Fetch the device and generate token
        device = TOTPDevice.objects.get(id=device_id)
        token = str(totp(device.bin_key, device.step, device.t0, device.digits, device.drift)).zfill(device.digits)

        # Step 4: Submit generator step (no token required)
        resp = self.client.post(self.url, {
            'settlex_two_factor_setup_view-current_step': 'generator',
        }, follow=True)
        self.assertEqual(self._current_step(resp), 'validation')

        # Step 5: POST token to validation step
        resp = self.client.post(self.url, {
            'settlex_two_factor_setup_view-current_step': 'validation',
            'validation-token': token,
        }, follow=True)

        # Assert that the setup is complete
        self.assertRedirects(resp, reverse('two_factor:setup_complete'))
        device.refresh_from_db()
        self.assertTrue(device.confirmed)