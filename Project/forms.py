from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import (
    StaffProfile,
    Location,
    Customer,
    FinancingApplication,
    Location,
    Document
)


class StaffLoginForm(AuthenticationForm):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('rep', 'Representative'),
        ('reviewer', 'Reviewer'),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username',
                'autocomplete': 'username'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your password',
                'autocomplete': 'current-password'
            }
        )
    )

    def clean(self):

        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        role = cleaned_data.get('role')

        if not username or not role:
            return cleaned_data

        try:
            user = self.get_user()

            if not user:
                return cleaned_data

            # -----------------------------
            # ADMIN
            # -----------------------------

            if role == 'admin':

                if not user.is_superuser:
                    raise forms.ValidationError(
                        'This account does not have Administrator access.'
                    )

            # -----------------------------
            # REPRESENTATIVE
            # -----------------------------

            elif role == 'rep':

                if not hasattr(user, 'staff_profile'):
                    raise forms.ValidationError(
                        'This account has not been assigned a staff role.'
                    )

                if user.staff_profile.role != 'rep':
                    raise forms.ValidationError(
                        'This account is not registered as a Representative.'
                    )

            # -----------------------------
            # REVIEWER
            # -----------------------------

            elif role == 'reviewer':

                if not hasattr(user, 'staff_profile'):
                    raise forms.ValidationError(
                        'This account has not been assigned a staff role.'
                    )

                if user.staff_profile.role != 'reviewer':
                    raise forms.ValidationError(
                        'This account is not registered as a Reviewer.'
                    )

        except forms.ValidationError:
            raise

        except Exception:
            raise forms.ValidationError(
                'Unable to verify your staff role. Please contact the administrator.'
            )

        return cleaned_data


# ==========================================================
# STAFF USER FORM
# ==========================================================

class StaffUserForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter first name"
            }
        )
    )

    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter last name"
            }
        )
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter email address"
            }
        )
    )

    role = forms.ChoiceField(
        choices=StaffProfile.ROLE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select"
            }
        )
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter phone number"
            }
        )
    )

    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True),
        required=False,
        empty_label="Select location",
        widget=forms.Select(
            attrs={
                "class": "form-select"
            }
        )
    )

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter username",
                "autocomplete": "off"
            }
        )
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter password",
                "autocomplete": "new-password"
            }
        )
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm password",
                "autocomplete": "new-password"
            }
        )
    )

    class Meta:

        model = User

        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone",
            "location",
            "password1",
            "password2",
        )

    def clean_username(self):

        username = self.cleaned_data["username"]

        if User.objects.filter(
            username__iexact=username
        ).exists():

            raise forms.ValidationError(
                "A user with this username already exists."
            )

        return username

    def save(self, commit=True):

        user = super().save(commit=commit)

        if commit:

            StaffProfile.objects.create(
                user=user,
                role=self.cleaned_data["role"],
                phone=self.cleaned_data["phone"],
                location=self.cleaned_data["location"]
            )

        return user


# ==========================================================
# STAFF USER UPDATE FORM
# ==========================================================

class StaffUserUpdateForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter first name"
            }
        )
    )

    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter last name"
            }
        )
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter email address"
            }
        )
    )

    role = forms.ChoiceField(
        choices=StaffProfile.ROLE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select"
            }
        )
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter phone number"
            }
        )
    )

    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True),
        required=False,
        empty_label="Select location",
        widget=forms.Select(
            attrs={
                "class": "form-select"
            }
        )
    )

    is_active = forms.BooleanField(
        required=False,
        label="Account is active"
    )

    class Meta:

        model = User

        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone",
            "location",
            "is_active",
        )

        widgets = {

            "username": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        profile, created = StaffProfile.objects.get_or_create(
            user=self.instance
        )

        self.fields["role"].initial = profile.role

        self.fields["phone"].initial = profile.phone

        self.fields["location"].initial = profile.location

    def save(self, commit=True):

        user = super().save(commit=commit)

        if commit:

            profile, created = StaffProfile.objects.get_or_create(
                user=user
            )

            profile.role = self.cleaned_data["role"]

            profile.phone = self.cleaned_data["phone"]

            profile.location = self.cleaned_data["location"]

            profile.save()

        return user


# ==========================================================
# LOCATION FORM
# ==========================================================

class LocationForm(forms.ModelForm):

    class Meta:

        model = Location

        fields = (
            "name",
            "zone",
            "description",
            "is_active",
        )

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter location name"
                }
            ),

            "zone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter zone or region"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Provide a brief description "
                        "of this location..."
                    )
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

        labels = {

            "name": "Location Name",

            "zone": "Zone / Region",

            "description": "Description",

            "is_active": "Location is Active",
        }

        help_texts = {

            "name": (
                "Use a clear and unique name "
                "for this location."
            ),

            "zone": (
                "Specify the operational zone "
                "or region."
            ),

            "is_active": (
                "Inactive locations cannot be "
                "assigned to new staff."
            ),
        }


# ==========================================================
# CUSTOMER FORM
# ==========================================================

class CustomerForm(forms.ModelForm):

    class Meta:

        model = Customer

        fields = [
            "customer_id",
            "first_name",
            "last_name",
            "business_name",
            "phone",
            "email",
            "location",
            "is_active",
        ]

        widgets = {

            "customer_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. ADX-CUS-0001",
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter first name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter last name",
                }
            ),

            "business_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter business name",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter email address",
                }
            ),

            "location": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

        labels = {

            "customer_id": "Customer ID",

            "first_name": "First Name",

            "last_name": "Last Name",

            "business_name": "Business Name",

            "phone": "Phone Number",

            "email": "Email Address",

            "location": "Operating Location",

            "is_active": "Active Customer",
        }

        help_texts = {

            "customer_id":
                "Enter a unique identifier for this customer.",

            "location":
                "Select the location associated with this customer.",

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["location"].queryset = (
            Location.objects.filter(
                is_active=True
            ).order_by("name")
        )

    def clean_customer_id(self):

        customer_id = self.cleaned_data["customer_id"].strip()

        return customer_id.upper()

    def clean_business_name(self):

        business_name = self.cleaned_data["business_name"].strip()

        return business_name


# ==========================================================
# FINANCING APPLICATION FORM
# ==========================================================

class FinancingApplicationForm(forms.ModelForm):

    class Meta:

        model = FinancingApplication

        fields = [
            "application_id",
            "customer",
            "application_type",
            "requested_amount",
            "notes",
        ]

        widgets = {

            "application_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter application ID",
                    "autocomplete": "off",
                }
            ),

            "customer": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "application_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "requested_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter requested amount",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Enter any additional information "
                        "about this financing application..."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        if user is not None:

            self.fields["customer"].queryset = (
                self.fields["customer"].queryset
                .filter(registered_by=user)
                .order_by("business_name")
            )


# ==========================================================
# REVIEW APPLICATION FORM
# ==========================================================

class ReviewerApplicationForm(forms.ModelForm):

    class Meta:

        model = FinancingApplication

        fields = [
            "approved_amount",
            "status",
            "notes",
        ]

        widgets = {

            "approved_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter approved amount",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": (
                        "Enter review notes, "
                        "approval comments or "
                        "reason for decline..."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["status"].choices = [

            ("review", "Under Review"),

            ("approved", "Approved"),

            ("declined", "Declined"),

        ]

# ==========================================================
# DOCUMENT FORM
# ==========================================================

class DocumentForm(forms.ModelForm):

    class Meta:

        model = Document

        fields = [
            "application",
            "document_type",
            "title",
            "file",
            "description",
        ]

        widgets = {

            "application": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "document_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "e.g. Business Bank Statement"
                    ),
                }
            ),

            "file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": (
                        ".pdf,"
                        ".jpg,"
                        ".jpeg,"
                        ".png,"
                        ".doc,"
                        ".docx"
                    ),
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Briefly describe this document..."
                    ),
                }
            ),
        }

    def clean_file(self):

        uploaded_file = self.cleaned_data.get("file")

        if not uploaded_file:
            raise forms.ValidationError(
                "Please select a document to upload."
            )

        allowed_extensions = [
            "pdf",
            "jpg",
            "jpeg",
            "png",
            "doc",
            "docx",
        ]

        extension = (
            uploaded_file.name
            .split(".")[-1]
            .lower()
        )

        if extension not in allowed_extensions:

            raise forms.ValidationError(
                "Unsupported file type. "
                "Allowed formats: PDF, JPG, JPEG, "
                "PNG, DOC and DOCX."
            )

        max_size = 10 * 1024 * 1024

        if uploaded_file.size > max_size:

            raise forms.ValidationError(
                "File size must not exceed 10 MB."
            )

        return uploaded_file