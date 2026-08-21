from django.db import models
from django.contrib.auth.models import User

# ==========================================================
# LOCATION
# ==========================================================

class Location(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True
    )

    zone = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = "Location"

        verbose_name_plural = "Locations"

        ordering = ["name"]

    def __str__(self):

        if self.zone:

            return f"{self.name} - {self.zone}"

        return self.name


# ==========================================================
# STAFF PROFILE
# ==========================================================

class StaffProfile(models.Model):

    ROLE_CHOICES = (

        ("rep", "Representative"),

        ("reviewer", "Reviewer"),

    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="staff_profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_members"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = "Staff Profile"

        verbose_name_plural = "Staff Profiles"

        ordering = ["-created_at"]

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.get_role_display()}"
        )


# ==========================================================
# CUSTOMER
# ==========================================================

class Customer(models.Model):

    customer_id = models.CharField(
        max_length=50,
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    business_name = models.CharField(
        max_length=200
    )

    phone = models.CharField(
        max_length=20
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customers"
    )

    registered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registered_customers"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = "Customer"

        verbose_name_plural = "Customers"

        ordering = ["-created_at"]

    def __str__(self):

        return (
            f"{self.business_name} "
            f"({self.customer_id})"
        )

    @property
    def full_name(self):

        return f"{self.first_name} {self.last_name}"

    @property
    def application_count(self):

        return self.applications.count()



# ==========================================================
# FINANCING APPLICATION
# ==========================================================

class FinancingApplication(models.Model):

    APPLICATION_TYPES = (

        ("credit", "Credit Financing"),

        ("inventory", "Inventory Financing"),

    )

    STATUS_CHOICES = (

        ("draft", "Draft"),

        ("submitted", "Submitted"),

        ("verification", "Under Verification"),

        ("verified", "Verified"),

        ("review", "Under Review"),

        ("approved", "Approved"),

        ("declined", "Declined"),

        ("disbursed", "Disbursed"),

        ("completed", "Completed"),

    )

    application_id = models.CharField(
        max_length=50,
        unique=True
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    application_type = models.CharField(
        max_length=20,
        choices=APPLICATION_TYPES
    )

    requested_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    approved_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="draft"
    )

    assigned_rep = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_applications"
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_applications"
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = "Financing Application"

        verbose_name_plural = "Financing Applications"

        ordering = ["-created_at"]

    def __str__(self):

        return self.application_id


# ==========================================================
# DOCUMENT
# ==========================================================

class Document(models.Model):

    DOCUMENT_TYPE_CHOICES = (

        ("identification", "Identification Document"),

        ("business_registration", "Business Registration"),

        ("bank_statement", "Bank Statement"),

        ("proof_of_address", "Proof of Address"),

        ("invoice", "Invoice / Quotation"),

        ("guarantor", "Guarantor Document"),

        ("supplier", "Supplier Document"),

        ("payment_confirmation", "Payment Confirmation"),

        ("other", "Other"),

    )

    STATUS_CHOICES = (

        ("pending", "Pending Review"),

        ("verified", "Verified"),

        ("rejected", "Rejected"),

    )

    application = models.ForeignKey(
        FinancingApplication,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES
    )

    title = models.CharField(
        max_length=200
    )

    file = models.FileField(
        upload_to="documents/%Y/%m/"
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents"
    )

    review_note = models.TextField(
        blank=True,
        null=True
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_documents"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = "Document"

        verbose_name_plural = "Documents"

        ordering = ["-created_at"]

    def __str__(self):

        return (
            f"{self.title} - "
            f"{self.application.application_id}"
        )

    @property
    def file_extension(self):

        if self.file:

            return self.file.name.split(".")[-1].upper()

        return ""

    @property
    def file_name(self):

        if self.file:

            return self.file.name.split("/")[-1]

        return ""


# ==========================================================
# AUDIT LOG
# ==========================================================

class AuditLog(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs"
    )

    action = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        verbose_name = "Audit Log"

        verbose_name_plural = "Audit Logs"

        ordering = ["-created_at"]

    def __str__(self):

        return (
            f"{self.action} - "
            f"{self.created_at:%Y-%m-%d %H:%M}"
        )