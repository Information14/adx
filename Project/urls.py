from django.urls import path, include

from . import views

from .views import (
    BaseView, 
    
    StaffLoginView,
    StaffLogoutView,
    
    AdminDashboardView,
    RepDashboardView,
    ReviewerDashboardView,
    
    StaffUserListView,
    StaffUserCreateView,
    StaffUserUpdateView, 
    StaffUserToggleStatusView, 

    LocationListView,
    LocationCreateView,

    ApplicationListView,
    ApplicationDetailView,
    ApplicationCreateView,
    ApplicationReviewView, 

    CustomerListView,
    CustomerCreateView,
    CustomerDetailView,
    
    
    ReviewerDashboardView,
    ReviewerApplicationListView,
    ReviewerApplicationUpdateView,
    
    
    DocumentListView,
    DocumentCreateView,
    DocumentDetailView,
)

urlpatterns = [
    
    path(
        "",
        BaseView.as_view(),
        name="index"
    ),

    path(
        "login/",
        StaffLoginView.as_view(),
        name="login"
    ),

    path(
        "logout/",
        StaffLogoutView.as_view(),
        name="logout"
    ),

    path(
        "dashboard/admin/",
        AdminDashboardView.as_view(),
        name="admin_dashboard"
    ),

    path(
        "users/",
        StaffUserListView.as_view(),
        name="user_list"
    ),

    path(
        "users/create/",
        StaffUserCreateView.as_view(),
        name="user_create"
    ),

    path(
        "users/<int:pk>/edit/",
        StaffUserUpdateView.as_view(),
        name="user_edit"
    ),

    path(
        "users/<int:pk>/toggle-status/",
        StaffUserToggleStatusView.as_view(),
        name="user_toggle_status"
    ),
    

    path(
        "locations/",
        LocationListView.as_view(),
        name="location_list"
    ),

    path(
        "locations/create/",
        LocationCreateView.as_view(),
        name="location_create"
    ),


    path(
        "applications/",
        ApplicationListView.as_view(),
        name="application_list"
    ),

    path(
        "applications/create/",
        ApplicationCreateView.as_view(),
        name="application_create"
    ),

    path(
        "applications/<int:pk>/",
        ApplicationDetailView.as_view(),
        name="application_detail"
    ),

    path(
        "applications/<int:pk>/review/",
        ApplicationReviewView.as_view(),
        name="application_review"
    ),


    path(
        "customers/",
        CustomerListView.as_view(),
        name="customer_list"
    ),

    path(
        "customers/create/",
        CustomerCreateView.as_view(),
        name="customer_create"
    ),

    path(
        "customers/<int:pk>/",
        CustomerDetailView.as_view(),
        name="customer_detail"
    ),
    

    path(
        "dashboard/rep/",
        RepDashboardView.as_view(),
        name="rep_dashboard"
    ),

    path(
        "dashboard/reviewer/",
        ReviewerDashboardView.as_view(),
        name="reviewer_dashboard"
    ),
    
    
    # ======================================================
    # REVIEWER DASHBOARD
    # ======================================================

    path(
        "dashboard/reviewer/",
        ReviewerDashboardView.as_view(),
        name="reviewer_dashboard"
    ),


    # ======================================================
    # REVIEWER APPLICATIONS
    # ======================================================

    path(
        "reviewer/applications/",
        ReviewerApplicationListView.as_view(),
        name="reviewer_applications"
    ),


    path(
        "reviewer/applications/<int:pk>/review/",
        ReviewerApplicationUpdateView.as_view(),
        name="reviewer_application_review"
    ),
    
    
    # ==========================================================
    # DOCUMENTS
    # ==========================================================

    path(
        "documents/",
        DocumentListView.as_view(),
        name="document_list"
    ),

    path(
        "documents/upload/",
        DocumentCreateView.as_view(),
        name="document_create"
    ),

    path(
        "documents/<int:pk>/",
        DocumentDetailView.as_view(),
        name="document_detail"
    ),
    

]
