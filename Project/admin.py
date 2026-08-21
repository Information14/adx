from django.contrib import admin

from .models import (
    StaffProfile,
    Location,
    Customer,
    FinancingApplication,
    AuditLog,
    Document
)

# ==========================================================
# STAFF PROFILE
# ==========================================================

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "role",
        "phone",
        "location",
        "created_at",
    )

    list_filter = (
        'role',
        'location',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        "phone",
    )

    
    autocomplete_fields = (
        "user",
        "location",
    )

    ordering = (
        "-created_at",
    )
    
    
# ==========================================================
# LOCATION ADMIN
# ==========================================================

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "zone",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "zone",
    )

    search_fields = (
        "name",
        "zone",
        "description",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ==========================================================
# CUSTOMER
# ==========================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "customer_id",
        "business_name",
        "first_name",
        "last_name",
        "phone",
        "location",
        "registered_by",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "location",
        "created_at",
    )

    search_fields = (
        "customer_id",
        "business_name",
        "first_name",
        "last_name",
        "phone",
        "email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25


# ==========================================================
# FINANCING APPLICATION
# ==========================================================

@admin.register(FinancingApplication)
class FinancingApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "application_id",
        "customer",
        "application_type",
        "requested_amount",
        "approved_amount",
        "status",
        "assigned_rep",
        "reviewer",
        "created_at",
    )

    list_filter = (
        "application_type",
        "status",
    )

    search_fields = (
        "application_id",
        "customer__business_name",
        "customer__customer_id",
        "assigned_rep__username",
        "reviewer__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# ==========================================================
# DOCUMENT
# ==========================================================

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "application",
        "document_type",
        "status",
        "uploaded_by",
        "reviewed_by",
        "created_at",
    )

    list_filter = (
        "document_type",
        "status",
        "created_at",
    )

    search_fields = (
        "title",
        "application__application_id",
        "application__customer__business_name",
        "application__customer__customer_id",
    )

    readonly_fields = (
        "uploaded_by",
        "reviewed_by",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# ==========================================================
# AUDIT LOG
# ==========================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "action",
        "created_at",
    )

    list_filter = (
        "action",
        "created_at",
    )

    search_fields = (
        "user__username",
        "action",
        "description",
    )

    readonly_fields = (
        "user",
        "action",
        "description",
        "created_at",
    )

    ordering = (
        "-created_at",
    )