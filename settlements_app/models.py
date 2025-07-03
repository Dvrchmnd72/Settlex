import uuid
import logging
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import localtime
import pytz

logger = logging.getLogger(__name__)

def generate_file_reference():
    return str(uuid.uuid4()).split('-')[0].upper()

class Firm(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField()
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    acn = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, default="")
    postcode = models.CharField(max_length=10, blank=True, default="")
    state = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return self.name

PROFESSION_CHOICES = [
    ('solicitor', 'Solicitor'),
    ('conveyancer', 'Conveyancer'),
    ('other', 'Other'),
]

class Solicitor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="solicitor")
    instructing_solicitor = models.CharField(max_length=255)
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE, related_name="solicitors", null=True, blank=True)
    office_phone = models.CharField(max_length=20, blank=True, null=True)
    mobile_phone = models.CharField(max_length=20, blank=True, null=True)
    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES, default='solicitor')
    law_society_number = models.CharField(max_length=50, blank=True, null=True)
    conveyancer_license = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.instructing_solicitor} ({self.firm.name if self.firm else 'No Firm'})"

PROPERTY_TYPE_CHOICES = [
    ('house', 'House'),
    ('unit', 'Unit/Townhouse'),
    ('vacant_land', 'Vacant Land'),
    ('commercial', 'Commercial'),
    ('other', 'Other'),
]

SETTLEMENT_CHOICES = [
    ("purchase", "Purchase"),
    ("sale", "Sale"),
    ("lodge_mortgage", "Register Mortgage"),
    ("discharge_mortgage", "Discharge Mortgage"),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('ready', 'Ready'),
    ('settling', 'Settling'),
    ('settled', 'Settled'),
]

class Instruction(models.Model):
    solicitor = models.ForeignKey(Solicitor, on_delete=models.CASCADE, related_name="instructions")
    file_reference = models.CharField(max_length=50, unique=True, default=generate_file_reference)
    purchaser_name = models.CharField(max_length=255, blank=True, null=True)
    purchaser_email = models.EmailField(blank=True, null=True)
    purchaser_address = models.CharField(max_length=255, blank=True, null=True)
    purchaser_mobile = models.CharField(max_length=20, blank=True, null=True)
    seller_name = models.CharField(max_length=255, blank=True, null=True)
    seller_address = models.CharField(max_length=255, blank=True, null=True)
    title_search = models.CharField(max_length=255, blank=True, null=True)
    settlement_type = models.CharField(max_length=100, choices=SETTLEMENT_CHOICES, default="purchase")
    settlement_date = models.DateField(blank=True, null=True)
    lodgement_date = models.DateField(blank=True, null=True)
    settlement_time = models.TimeField(blank=True, null=True)
    title_reference = models.TextField(blank=False, null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_created = models.DateTimeField(auto_now_add=True)

    # NEW transaction address breakdown fields
    transaction_street_number = models.CharField(max_length=20, blank=True, null=True)
    transaction_street_name = models.CharField(max_length=255, blank=True, null=True)
    transaction_suburb = models.CharField(max_length=100, blank=True, null=True)
    transaction_state = models.CharField(max_length=50, blank=True, null=True)
    transaction_postcode = models.CharField(max_length=10, blank=True, null=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, blank=True, null=True)

    # Company Details
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_abn = models.CharField(max_length=50, blank=True, null=True)
    company_acn = models.CharField(max_length=50, blank=True, null=True)
    company_address = models.CharField(max_length=255, blank=True, null=True)

    # Directors (max 5)
    director_1_name = models.CharField(max_length=255, blank=True, null=True)
    director_1_email = models.EmailField(blank=True, null=True)
    director_1_mobile = models.CharField(max_length=20, blank=True, null=True)
    director_1_address = models.CharField(max_length=255, blank=True, null=True)
    # directors 2-5 stay same...

    director_2_name = models.CharField(max_length=255, blank=True, null=True)
    director_2_email = models.EmailField(blank=True, null=True)
    director_2_mobile = models.CharField(max_length=20, blank=True, null=True)
    director_2_address = models.CharField(max_length=255, blank=True, null=True)

    director_3_name = models.CharField(max_length=255, blank=True, null=True)
    director_3_email = models.EmailField(blank=True, null=True)
    director_3_mobile = models.CharField(max_length=20, blank=True, null=True)
    director_3_address = models.CharField(max_length=255, blank=True, null=True)

    director_4_name = models.CharField(max_length=255, blank=True, null=True)
    director_4_email = models.EmailField(blank=True, null=True)
    director_4_mobile = models.CharField(max_length=20, blank=True, null=True)
    director_4_address = models.CharField(max_length=255, blank=True, null=True)

    director_5_name = models.CharField(max_length=255, blank=True, null=True)
    director_5_email = models.EmailField(blank=True, null=True)
    director_5_mobile = models.CharField(max_length=20, blank=True, null=True)
    director_5_address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.file_reference} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        logger.info(f"Saving Instruction: {self.file_reference}")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        logger.info(f"Deleting Instruction: {self.file_reference}")
        super().delete(*args, **kwargs)

DOCUMENT_TYPE_CHOICES = [
    ('contract', 'Contract'),
    ('title_search', 'Title Search'),
    ('id_verification', 'Verification of ID'),
    ('form_qro_d2', 'Form QRO D2'),
    ('trust_document', 'Trust Document'),
    ('asic_extract', 'ASIC Extract'),
    ('gst_withholding', 'GST Withholding'),
]

class Document(models.Model):
    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='settlements/documents/')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, default='contract')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.instruction.file_reference}"


class PaymentDirection(models.Model):
    """Stores payment direction amounts for an instruction."""

    instruction = models.OneToOneField(
        Instruction,
        on_delete=models.CASCADE,
        related_name="payment_direction",
    )
    registration_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    pexa_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )

    def total(self):
        return (self.registration_fee or 0) + (self.pexa_fee or 0)

    def __str__(self):
        return f"PaymentDirection for {self.instruction.file_reference}"

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def sender_name(self):
        if self.sender.is_superuser:
            return "Settlex"
        return self.sender.get_full_name() or self.sender.username

    def formatted_timestamp(self):
        brisbane_tz = pytz.timezone("Australia/Brisbane")
        return localtime(self.timestamp, brisbane_tz).strftime('%d %b %Y, %I:%M %p')

    def __str__(self):
        return f"{self.sender_name()} -> {self.recipient.username}: {self.message[:50] if self.message else 'File'}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    two_factor_authenticated = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'


class PaymentDirectionLineItem(models.Model):
    CATEGORY_CHOICES = [
        ('professional_fees', 'Professional Fees'),
        ('lodgement_fees', 'Lodgement Fees'),
        ('pexa_fees', 'PEXA Fees'),
        ('other', 'Other'),
    ]

    payment_direction = models.ForeignKey(
        PaymentDirection, on_delete=models.CASCADE, related_name="line_items"
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    bank_name = models.CharField(max_length=100, blank=True, default='')
    account_name = models.CharField(max_length=100, default='Unnamed Account')
    account_details = models.CharField(max_length=100, blank=True, default='')
    owner = models.CharField(max_length=100, blank=True, default='')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.get_category_display()} - {self.account_name}: ${self.amount}"


