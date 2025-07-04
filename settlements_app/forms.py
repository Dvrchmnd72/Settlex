import logging
from django import forms
from urllib.parse import quote
from django.contrib.auth.models import User
from .models import Instruction, Document, Firm, Solicitor, PaymentDirection, PaymentDirectionLineItem
from two_factor.forms import TOTPDeviceForm, AuthenticationTokenForm
from django.contrib.auth.forms import AuthenticationForm
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import base64
from io import BytesIO
from django.core.exceptions import ValidationError
from binascii import unhexlify, Error as BinasciiError



logger = logging.getLogger(__name__)

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    firm_name = forms.CharField(max_length=100)
    acn = forms.CharField(max_length=50, required=False)
    office_phone = forms.CharField(max_length=20)
    mobile_phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255)
    postcode = forms.CharField(max_length=10)
    state = forms.CharField(max_length=50)
    profession = forms.ChoiceField(choices=[('solicitor', 'Solicitor'), ('conveyancer', 'Conveyancer')])

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

class InstructionForm(forms.ModelForm):
    class Meta:
        model = Instruction
        fields = '__all__'
        widgets = {
            'settlement_date': forms.DateInput(attrs={'type': 'date'}),
            'lodgement_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        logger.info(f"Saving InstructionForm for file reference: {self.cleaned_data.get('file_reference')}")
        instruction = super().save(commit=False)
        if commit:
            instruction.save()
            logger.info(f"Instruction '{instruction.file_reference}' saved successfully.")
        return instruction

    def clean_file_reference(self):
        file_reference = self.cleaned_data.get('file_reference')
        if Instruction.objects.filter(file_reference=file_reference).exists():
            raise forms.ValidationError('This file reference already exists. Please choose a different one.')
        return file_reference

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'file']

    def save(self, instruction_instance, commit=True):
        document = super().save(commit=False)
        document.instruction = instruction_instance
        if commit:
            document.save()
            logger.info(f"Document '{document.name}' uploaded for instruction {document.instruction.file_reference}")
        return document


class PaymentDirectionForm(forms.ModelForm):
    class Meta:
        model = PaymentDirection
        fields = ['registration_fee', 'pexa_fee']

class DummyForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        logger.debug("👤 DummyForm initialized with user: %s", self.user)
        super().__init__(*args, **kwargs)

class WelcomeStepForm(DummyForm):
    pass

class ValidationStepForm(AuthenticationTokenForm):
    def __init__(self, *args, user=None, device=None, **kwargs):
        self.user = user
        self.device = device
        logger.debug("🔐 ValidationStepForm initialized with user: %s and device: %s", self.user, self.device)
        super().__init__(self.user, self.device, *args, **kwargs)

    def clean_token(self):
        token = self.cleaned_data.get("token")
        logger.debug("📅 Token received for validation: %s", token)

        if not self.device:
            logger.warning("⚠️ No device assigned to ValidationStepForm.")
            raise ValidationError("Internal error: device missing.")

        if not self.device.verify_token(token):
            logger.warning("❌ Invalid token entered for device ID: %s", self.device.id)
            raise ValidationError("Entered token is not valid. Please check your device time and try again.")

        logger.info("✅ Token validated for device ID: %s", self.device.id)
        return token

    def save(self):
        if self.device:
            self.device.confirmed = True
            self.device.save()
            logger.info("✅ Device %s confirmed and saved", self.device.id)
        return self.device

class CustomTOTPDeviceForm(forms.Form):
    def __init__(self, *args, user=None, device=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = device
        logger.debug("🛠 CustomTOTPDeviceForm INIT: device=%s", self.device)

        self.qr_code = None
        self.secret_b32 = None
        if self.device:
            try:
                key_bytes = unhexlify(self.device.key.encode())
                self.secret_b32 = base64.b32encode(key_bytes).decode("utf-8").replace("=", "")
                issuer = "Settlex"
                label = quote(f"{issuer}:{self.device.user.email}")
                config_url = (
                    f"otpauth://totp/{label}?secret={self.secret_b32}"
                    f"&issuer={issuer}&algorithm=SHA1&digits=6&period=30"
                )

                qr = qrcode.make(config_url)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                self.qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")

                logger.debug("📱 QR code generated for: %s", config_url)
            except BinasciiError:
                logger.error("🚨 Device key is not a valid hex string: %s", self.device.key)
            except Exception:
                logger.exception("⚠️ Failed to generate QR code")

    def save(self):
        return self.device

    def get_context_data(self):
        context = {
            'qr_code_base64': self.qr_code,
            'totp_secret': self.secret_b32,
        }
        logger.debug("📱 CustomTOTPDeviceForm.get_context_data(): %s", context)
        return context

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email or Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })

class AdjustmentsForm(forms.Form):
    period_from = forms.DateField(label='Period From', widget=forms.DateInput(attrs={'type': 'date'}))
    period_to = forms.DateField(label='Period To', widget=forms.DateInput(attrs={'type': 'date'}))
    total_amount = forms.DecimalField(label='Total Amount', max_digits=10, decimal_places=2)
    payment_status = forms.ChoiceField(label='Payment Status', choices=[
        ('paid', 'Paid'),
        ('adjusted', 'Adjusted as Paid'),
        ('owing', 'Owing'),
    ])
    payable_by = forms.ChoiceField(label='Payable By', choices=[
        ('purchaser', 'Purchaser'),
        ('seller', 'Seller'),
    ])

    def __init__(self, *args, adjustment_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.adjustment_type = adjustment_type

        if self.adjustment_type == 'rates':
            self.fields['total_amount'].label = 'Total Amount of Rates Payable'
        elif self.adjustment_type == 'water':
            self.fields['total_amount'].label = 'Total Amount of Water Fees'
        elif self.adjustment_type == 'body_corporate':
            self.fields['total_amount'].label = 'Total Amount of Body Corporate Fees'
        # Add more elif conditions for other adjustment types as needed


class SettlementCalculatorForm(forms.Form):
    """Form for capturing settlement calculator inputs."""

    settlement_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    adjustment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    contract_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    contract_price = forms.DecimalField(
        required=False, max_digits=12, decimal_places=2
    )

    settlement_place = forms.CharField(required=False)
    settlement_time = forms.CharField(required=False)

    deposit = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )
    release_mortgage_fee = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )

    registration_fee = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )

    pexa_fee = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )

    council_start = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    council_end = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    council_amount = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )

    water_start = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    water_end = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    water_amount = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )

    # Body corporate levies
    admin_start = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    admin_end = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    admin_amount = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )

    sinking_start = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    sinking_end = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    sinking_amount = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )

    insurance_start = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    insurance_end = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    insurance_amount = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )

    special_start = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    special_end = forms.DateField(
        required=False, widget=forms.DateInput(attrs={'type': 'date'})
    )
    special_amount = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )


class PaymentDirectionLineItemForm(forms.ModelForm):
    class Meta:
        model = PaymentDirectionLineItem
        fields = [
            'category',
            'bank_name',
            'account_name',
            'account_details',
            'owner',
            'amount',
            'direction_type',  # 👈 Add this field
        ]

