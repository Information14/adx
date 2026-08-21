from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    DetailView,
    UpdateView
)

from .forms import (
    StaffLoginForm,
    StaffUserForm,
    StaffUserUpdateForm, 
    LocationForm,
    CustomerForm,
    FinancingApplicationForm,
    DocumentForm, 
)

from .models import (
    StaffProfile,
    Location,
    Customer,
    FinancingApplication,
    AuditLog,
    Document
)

from django.contrib import messages


from .forms import ReviewerApplicationForm



# ==========================================================
# BASE VIEW
# ==========================================================

class BaseView(TemplateView):

    template_name = "base.html"
    

# ==========================================================
# STAFF LOGIN
# ==========================================================

class StaffLoginView(LoginView):

    template_name = "registration/login.html"

    authentication_form = StaffLoginForm

    redirect_authenticated_user = True

    def get_success_url(self):

        user = self.request.user

        if user.is_superuser:
            return reverse_lazy("admin_dashboard")

        if hasattr(user, "staff_profile"):

            role = user.staff_profile.role

            if role == "rep":
                return reverse_lazy("rep_dashboard")

            if role == "reviewer":
                return reverse_lazy("reviewer_dashboard")

        return reverse_lazy("login")


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

class AdminDashboardView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    TemplateView
):

    template_name = "dashboard/admin_dashboard.html"

    login_url = reverse_lazy("login")

    def test_func(self):

        return self.request.user.is_superuser

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["total_staff"] = User.objects.filter(
            is_superuser=False
        ).count()

        context["total_reps"] = StaffProfile.objects.filter(
            role="rep"
        ).count()

        context["total_reviewers"] = StaffProfile.objects.filter(
            role="reviewer"
        ).count()

        context["total_locations"] = Location.objects.count()

        context["total_customers"] = Customer.objects.count()

        context["total_applications"] = (
            FinancingApplication.objects.count()
        )

        context["pending_applications"] = (
            FinancingApplication.objects.filter(
                status__in=[
                    "submitted",
                    "verification",
                    "review",
                ]
            ).count()
        )

        context["approved_applications"] = (
            FinancingApplication.objects.filter(
                status="approved"
            ).count()
        )

        context["recent_applications"] = (
            FinancingApplication.objects
            .select_related("customer")
            .order_by("-created_at")[:6]
        )

        context["recent_audit_logs"] = (
            AuditLog.objects
            .select_related("user")
            .order_by("-created_at")[:6]
        )

        return context



# ==========================================================
# LOCATION LIST
# ==========================================================

class LocationListView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    ListView
):

    model = Location

    template_name = "locations/location_list.html"

    context_object_name = "locations"

    login_url = reverse_lazy("login")

    def test_func(self):

        return self.request.user.is_superuser

    def get_queryset(self):

        queryset = Location.objects.all()

        search = self.request.GET.get(
            "search",
            ""
        ).strip()

        zone = self.request.GET.get(
            "zone",
            ""
        ).strip()

        status = self.request.GET.get(
            "status",
            ""
        ).strip()

        if search:

            queryset = queryset.filter(
                name__icontains=search
            )

        if zone:

            queryset = queryset.filter(
                zone__icontains=zone
            )

        if status == "active":

            queryset = queryset.filter(
                is_active=True
            )

        elif status == "inactive":

            queryset = queryset.filter(
                is_active=False
            )

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(
            **kwargs
        )

        context["total_locations"] = (
            Location.objects.count()
        )

        context["active_locations"] = (
            Location.objects.filter(
                is_active=True
            ).count()
        )

        context["inactive_locations"] = (
            Location.objects.filter(
                is_active=False
            ).count()
        )

        context["zones"] = (
            Location.objects
            .exclude(zone__isnull=True)
            .exclude(zone="")
            .values_list("zone", flat=True)
            .distinct()
            .order_by("zone")
        )

        return context


# ==========================================================
# CREATE LOCATION
# ==========================================================

class LocationCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView
):

    model = Location

    form_class = LocationForm

    template_name = "locations/location_form.html"

    success_url = reverse_lazy(
        "location_list"
    )

    login_url = reverse_lazy(
        "login"
    )

    def test_func(self):

        return self.request.user.is_superuser

    def form_valid(self, form):

        response = super().form_valid(form)

        AuditLog.objects.create(

            user=self.request.user,

            action="Location created",

            description=(
                f"Location '{self.object.name}' "
                f"was created by "
                f"{self.request.user.username}."
            )
        )

        messages.success(
            self.request,
            (
                f"Location '{self.object.name}' "
                "was created successfully."
            )
        )

        return response

    def form_invalid(self, form):

        messages.error(
            self.request,
            "Please correct the errors below."
        )

        return super().form_invalid(form)


# ==========================================================
# APPLICATION LIST
# ==========================================================

class ApplicationListView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    ListView
):

    model = FinancingApplication

    template_name = "applications/application_list.html"

    context_object_name = "applications"

    login_url = reverse_lazy("login")

    def test_func(self):

        user = self.request.user

        if user.is_superuser:
            return True

        return (
            hasattr(user, "staff_profile")
            and user.staff_profile.role in [
                "rep",
                "reviewer",
            ]
        )

    def get_queryset(self):

        user = self.request.user

        queryset = (
            FinancingApplication.objects
            .select_related(
                "customer",
                "assigned_rep",
                "reviewer",
            )
            .order_by("-created_at")
        )

        # --------------------------------------------------
        # ADMIN
        # --------------------------------------------------

        if user.is_superuser:

            return queryset

        # --------------------------------------------------
        # REPRESENTATIVE
        # --------------------------------------------------

        if (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "rep"
        ):

            return queryset.filter(
                assigned_rep=user
            )

        # --------------------------------------------------
        # REVIEWER
        # --------------------------------------------------

        if (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "reviewer"
        ):

            return queryset.filter(
                reviewer=user
            )

        return queryset.none()

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )


# ==========================================================
# APPLICATION DETAIL
# ==========================================================

class ApplicationDetailView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DetailView
):

    model = FinancingApplication

    template_name = "applications/application_detail.html"

    context_object_name = "application"

    login_url = reverse_lazy("login")

    def get_queryset(self):

        user = self.request.user

        queryset = (
            FinancingApplication.objects
            .select_related(
                "customer",
                "assigned_rep",
                "reviewer",
            )
        )

        # --------------------------------------------------
        # ADMIN
        # --------------------------------------------------

        if user.is_superuser:

            return queryset

        # --------------------------------------------------
        # REPRESENTATIVE
        # --------------------------------------------------

        if (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "rep"
        ):

            return queryset.filter(
                assigned_rep=user
            )

        # --------------------------------------------------
        # REVIEWER
        # --------------------------------------------------

        if (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "reviewer"
        ):

            return queryset.filter(
                reviewer=user
            )

        return queryset.none()

    def test_func(self):

        return self.get_queryset().filter(
            pk=self.kwargs["pk"]
        ).exists()

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )


# ==========================================================
# CREATE APPLICATION
# ==========================================================

class ApplicationCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView
):

    model = FinancingApplication

    form_class = FinancingApplicationForm

    template_name = "applications/application_form.html"

    success_url = reverse_lazy("application_list")

    login_url = reverse_lazy("login")

    def test_func(self):

        user = self.request.user

        return (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "rep"
        )

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs

    def form_valid(self, form):

        form.instance.assigned_rep = self.request.user

        form.instance.status = "draft"

        response = super().form_valid(form)

        AuditLog.objects.create(

            user=self.request.user,

            action="Financing application created",

            description=(
                f"Application "
                f"'{self.object.application_id}' "
                f"was created by "
                f"'{self.request.user.username}'."
            )
        )

        return response

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )


# ==========================================================
# REVIEW APPLICATION
# ==========================================================

class ApplicationReviewView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):

    model = FinancingApplication

    form_class = ReviewerApplicationForm

    template_name = "applications/application_form.html"

    login_url = reverse_lazy("login")

    def test_func(self):

        user = self.request.user

        if user.is_superuser:

            return True

        if not hasattr(user, "staff_profile"):

            return False

        if user.staff_profile.role != "reviewer":

            return False

        application = self.get_object()

        return (
            application.reviewer == user
            or application.reviewer is None
        )

    def form_valid(self, form):

        if not self.object.reviewer:

            form.instance.reviewer = self.request.user

        response = super().form_valid(form)

        AuditLog.objects.create(

            user=self.request.user,

            action="Financing application reviewed",

            description=(
                f"Application "
                f"'{self.object.application_id}' "
                f"was updated by "
                f"'{self.request.user.username}'. "
                f"Status: "
                f"'{self.object.get_status_display()}'."
            )
        )

        return response

    def get_success_url(self):

        return reverse_lazy(
            "application_detail",
            kwargs={
                "pk": self.object.pk
            }
        )

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )



# ==========================================================
# CREATE CUSTOMER
# ==========================================================

class CustomerCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView
):

    model = Customer

    form_class = CustomerForm

    template_name = "customers/customer_form.html"

    success_url = reverse_lazy("customer_list")

    login_url = reverse_lazy("login")

    def test_func(self):

        user = self.request.user

        return (
            user.is_authenticated
            and hasattr(user, "staff_profile")
            and user.staff_profile.role == "rep"
        )

    def form_valid(self, form):

        form.instance.registered_by = self.request.user

        response = super().form_valid(form)

        AuditLog.objects.create(
            user=self.request.user,

            action="Customer created",

            description=(
                f"Customer "
                f"'{self.object.business_name}' "
                f"({self.object.customer_id}) "
                f"was created by "
                f"'{self.request.user.username}'."
            )
        )

        return response

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )
        


# ==========================================================
# CUSTOMER LIST
# ==========================================================

class CustomerListView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    ListView
):

    model = Customer

    template_name = "customers/customer_list.html"

    context_object_name = "customers"

    login_url = reverse_lazy("login")

    paginate_by = 10

    def test_func(self):

        user = self.request.user

        # --------------------------------------------------
        # ADMIN
        # --------------------------------------------------

        if user.is_superuser:

            return True

        # --------------------------------------------------
        # REPRESENTATIVE
        # --------------------------------------------------

        return (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "rep"
        )

    def get_queryset(self):

        user = self.request.user

        # --------------------------------------------------
        # ADMIN SEES ALL CUSTOMERS
        # --------------------------------------------------

        if user.is_superuser:

            return Customer.objects.select_related(
                "location",
                "registered_by"
            ).order_by(
                "-created_at"
            )

        # --------------------------------------------------
        # REP SEES ONLY THEIR CUSTOMERS
        # --------------------------------------------------

        return Customer.objects.filter(
            registered_by=user
        ).select_related(
            "location"
        ).order_by(
            "-created_at"
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        customers = self.get_queryset()

        context["total_customers"] = customers.count()

        context["active_customers"] = customers.filter(
            is_active=True
        ).count()

        context["inactive_customers"] = customers.filter(
            is_active=False
        ).count()

        return context

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )
        
       # ==========================================================
# CUSTOMER DETAIL
# ==========================================================

class CustomerDetailView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DetailView
):

    model = Customer

    template_name = "customers/customer_detail.html"

    context_object_name = "customer"

    login_url = reverse_lazy("login")

    def get_queryset(self):

        user = self.request.user

        # --------------------------------------------------
        # ADMIN
        # --------------------------------------------------

        if user.is_superuser:

            return Customer.objects.select_related(
                "location",
                "registered_by"
            )

        # --------------------------------------------------
        # REP
        # --------------------------------------------------

        return Customer.objects.filter(
            registered_by=user
        ).select_related(
            "location"
        )

    def test_func(self):

        user = self.request.user

        customer = self.get_object()

        # --------------------------------------------------
        # ADMIN CAN VIEW ANY CUSTOMER
        # --------------------------------------------------

        if user.is_superuser:

            return True

        # --------------------------------------------------
        # REP CAN VIEW THEIR OWN CUSTOMER
        # --------------------------------------------------

        return (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "rep"
            and customer.registered_by == user
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["applications"] = (
            self.object.applications
            .all()
            .order_by("-created_at")
        )

        context["application_count"] = (
            self.object.applications.count()
        )

        return context

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        ) 
        

# ==========================================================
# LOGOUT
# ==========================================================

class StaffLogoutView(LogoutView):

    next_page = reverse_lazy("login")

# ==========================================================
# DASHBOARD REDIRECTION HELPER
# ==========================================================

def redirect_user_to_dashboard(user):

    # ------------------------------------------------------
    # ADMIN
    # ------------------------------------------------------

    if user.is_superuser:

        return redirect("admin_dashboard")

    # ------------------------------------------------------
    # STAFF ROLES
    # ------------------------------------------------------

    if hasattr(user, "staff_profile"):

        role = user.staff_profile.role

        if role == "rep":

            return redirect("rep_dashboard")

        if role == "reviewer":

            return redirect("reviewer_dashboard")

    # ------------------------------------------------------
    # FALLBACK
    # ------------------------------------------------------

    return redirect("login")

# ==========================================================
# REPRESENTATIVE DASHBOARD
# ==========================================================

class RepDashboardView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    TemplateView
):

    template_name = "dashboard/rep_dashboard.html"

    login_url = reverse_lazy("login")

    def test_func(self):

        user = self.request.user

        return (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "rep"
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        user = self.request.user

        # --------------------------------------------------
        # CUSTOMER DATA
        # --------------------------------------------------

        customers = Customer.objects.filter(
            registered_by=user
        )

        context["customer_count"] = customers.count()

        context["active_customer_count"] = customers.filter(
            is_active=True
        ).count()

        # --------------------------------------------------
        # APPLICATION DATA
        # --------------------------------------------------

        applications = FinancingApplication.objects.filter(
            assigned_rep=user
        )

        context["application_count"] = applications.count()

        context["pending_application_count"] = applications.filter(
            status__in=[
                "draft",
                "submitted",
                "verification",
                "review",
            ]
        ).count()

        context["approved_application_count"] = applications.filter(
            status="approved"
        ).count()

        context["disbursed_application_count"] = applications.filter(
            status="disbursed"
        ).count()

        # --------------------------------------------------
        # RECENT APPLICATIONS
        # --------------------------------------------------

        context["recent_applications"] = applications.select_related(
            "customer"
        ).order_by(
            "-created_at"
        )[:5]

        # --------------------------------------------------
        # RECENT CUSTOMERS
        # --------------------------------------------------

        context["recent_customers"] = customers.select_related(
            "location"
        ).order_by(
            "-created_at"
        )[:5]

        # --------------------------------------------------
        # STAFF PROFILE
        # --------------------------------------------------

        if hasattr(user, "staff_profile"):

            context["staff_profile"] = user.staff_profile

            context["staff_location"] = (
                user.staff_profile.location
            )

        return context

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )


# ==========================================================
# STAFF USER LIST
# ==========================================================

class StaffUserListView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    ListView, 
):

    model = User

    template_name = "users/user_list.html"

    context_object_name = "staff_users"

    login_url = reverse_lazy("login")

    paginate_by = 10

    def test_func(self):

        return self.request.user.is_superuser

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )

    def get_queryset(self):

        queryset = User.objects.filter(
            is_superuser=False
        ).select_related(
            "staff_profile",
            "staff_profile__location"
        ).order_by(
            "-date_joined"
        )

        search = self.request.GET.get(
            "search"
        )

        role = self.request.GET.get(
            "role"
        )

        status = self.request.GET.get(
            "status"
        )

        if search:

            queryset = queryset.filter(

                username__icontains=search

            ) | queryset.filter(

                first_name__icontains=search

            ) | queryset.filter(

                last_name__icontains=search

            ) | queryset.filter(

                email__icontains=search

            )

        if role in ["rep", "reviewer"]:

            queryset = queryset.filter(
                staff_profile__role=role
            )

        if status == "active":

            queryset = queryset.filter(
                is_active=True
            )

        elif status == "inactive":

            queryset = queryset.filter(
                is_active=False
            )

        return queryset


# ==========================================================
# CREATE STAFF USER
# ==========================================================

class StaffUserCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView
):

    model = User

    form_class = StaffUserForm

    template_name = "users/user_form.html"

    success_url = reverse_lazy(
        "user_list"
    )

    login_url = reverse_lazy("login")

    def test_func(self):

        return self.request.user.is_superuser

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(
            **kwargs
        )

        context["page_title"] = (
            "Create Staff User"
        )

        context["form_mode"] = "create"

        return context

    def form_valid(self, form):

        response = super().form_valid(form)

        AuditLog.objects.create(

            user=self.request.user,

            action="Staff user created",

            description=(
                f"Staff user "
                f"'{self.object.username}' "
                f"was created by "
                f"'{self.request.user.username}'."
            )
        )

        return response


# ==========================================================
# UPDATE STAFF USER
# ==========================================================

class StaffUserUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):

    model = User

    form_class = StaffUserUpdateForm

    template_name = "users/user_form.html"

    success_url = reverse_lazy(
        "user_list"
    )

    login_url = reverse_lazy("login")

    def test_func(self):

        return self.request.user.is_superuser

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )

    def get_queryset(self):

        return User.objects.filter(
            is_superuser=False
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(
            **kwargs
        )

        context["page_title"] = (
            "Update Staff User"
        )

        context["form_mode"] = "update"

        return context

    def form_valid(self, form):

        response = super().form_valid(form)

        AuditLog.objects.create(

            user=self.request.user,

            action="Staff user updated",

            description=(
                f"Staff user "
                f"'{self.object.username}' "
                f"was updated by "
                f"'{self.request.user.username}'."
            )
        )

        return response


# ==========================================================
# ACTIVATE / DEACTIVATE STAFF USER
# ==========================================================

class StaffUserToggleStatusView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    TemplateView
):

    login_url = reverse_lazy("login")

    def test_func(self):

        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):

        user = User.objects.filter(
            id=kwargs.get("pk"),
            is_superuser=False
        ).first()

        if user:

            user.is_active = not user.is_active

            user.save(
                update_fields=["is_active"]
            )

            status = (
                "activated"
                if user.is_active
                else "deactivated"
            )

            AuditLog.objects.create(

                user=request.user,

                action=f"Staff user {status}",

                description=(
                    f"Staff user "
                    f"'{user.username}' "
                    f"was {status} by "
                    f"'{request.user.username}'."
                )
            )

        return redirect("user_list")

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )


# ==========================================================
# REVIEWER DASHBOARD
# ==========================================================

class ReviewerDashboardView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    TemplateView
):

    template_name = "dashboard/reviewer_dashboard.html"

    login_url = reverse_lazy("login")

    def test_func(self):

        user = self.request.user

        return (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "reviewer"
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # --------------------------------------------------
        # APPLICATION STATISTICS
        # --------------------------------------------------

        context["verified_count"] = (
            FinancingApplication.objects.filter(
                status="verified"
            ).count()
        )

        context["review_count"] = (
            FinancingApplication.objects.filter(
                status="review"
            ).count()
        )

        context["approved_count"] = (
            FinancingApplication.objects.filter(
                status="approved"
            ).count()
        )

        context["declined_count"] = (
            FinancingApplication.objects.filter(
                status="declined"
            ).count()
        )

        context["disbursed_count"] = (
            FinancingApplication.objects.filter(
                status="disbursed"
            ).count()
        )

        # --------------------------------------------------
        # RECENT APPLICATIONS
        # --------------------------------------------------

        context["recent_applications"] = (
            FinancingApplication.objects
            .select_related("customer", "assigned_rep")
            .filter(
                status__in=[
                    "verified",
                    "review",
                    "approved",
                    "declined"
                ]
            )
            .order_by("-updated_at")[:8]
        )

        # --------------------------------------------------
        # APPLICATIONS AWAITING REVIEW
        # --------------------------------------------------

        context["pending_reviews"] = (
            FinancingApplication.objects
            .select_related("customer", "assigned_rep")
            .filter(
                status="verified"
            )
            .order_by("-updated_at")[:5]
        )

        # --------------------------------------------------
        # RECENT AUDIT ACTIVITY
        # --------------------------------------------------

        context["recent_activity"] = (
            AuditLog.objects
            .select_related("user")
            .order_by("-created_at")[:6]
        )

        return context

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )


# ==========================================================
# VERIFIED APPLICATIONS
# ==========================================================

class ReviewerApplicationListView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    ListView
):

    model = FinancingApplication

    template_name = (
        "applications/application_list.html"
    )

    context_object_name = "applications"

    login_url = reverse_lazy("login")

    def test_func(self):

        user = self.request.user

        return (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "reviewer"
        )

    def get_queryset(self):

        return (
            FinancingApplication.objects
            .select_related(
                "customer",
                "assigned_rep"
            )
            .filter(
                status__in=[
                    "verified",
                    "review",
                    "approved",
                    "declined"
                ]
            )
            .order_by("-updated_at")
        )

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )


# ==========================================================
# REVIEW APPLICATION
# ==========================================================

class ReviewerApplicationUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):

    model = FinancingApplication

    form_class = ReviewerApplicationForm

    template_name = (
        "applications/application_form.html"
    )

    pk_url_kwarg = "pk"

    login_url = reverse_lazy("login")

    def test_func(self):

        user = self.request.user

        return (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "reviewer"
        )

    def form_valid(self, form):

        application = form.save(
            commit=False
        )

        application.reviewer = (
            self.request.user
        )

        application.save()

        AuditLog.objects.create(

            user=self.request.user,

            action="Application reviewed",

            description=(
                f"Application "
                f"'{application.application_id}' "
                f"was updated by reviewer "
                f"'{self.request.user.username}'."
            )
        )

        return redirect(
            "reviewer_applications"
        )

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )

# ==========================================================
# DOCUMENT LIST
# ==========================================================

class DocumentListView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    ListView
):

    model = Document

    template_name = "documents/document_list.html"

    context_object_name = "documents"

    login_url = reverse_lazy("login")

    def test_func(self):

        user = self.request.user

        if user.is_superuser:
            return True

        return (
            hasattr(user, "staff_profile")
            and user.staff_profile.role in [
                "rep",
                "reviewer",
            ]
        )

    def get_queryset(self):

        user = self.request.user

        queryset = (
            Document.objects
            .select_related(
                "application",
                "application__customer",
                "uploaded_by",
                "reviewed_by",
            )
        )

        # ------------------------------------------
        # ADMIN
        # ------------------------------------------

        if user.is_superuser:

            return queryset.order_by(
                "-created_at"
            )

        # ------------------------------------------
        # REPRESENTATIVE
        # ------------------------------------------

        if (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "rep"
        ):

            return queryset.filter(
                application__assigned_rep=user
            ).order_by(
                "-created_at"
            )

        # ------------------------------------------
        # REVIEWER
        # ------------------------------------------

        if (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "reviewer"
        ):

            return queryset.filter(
                application__reviewer=user
            ).order_by(
                "-created_at"
            )

        return Document.objects.none()

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )

# ==========================================================
# DOCUMENT CREATE
# ==========================================================

class DocumentCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView
):

    model = Document

    form_class = DocumentForm

    template_name = "documents/document_form.html"

    success_url = reverse_lazy(
        "document_list"
    )

    login_url = reverse_lazy("login")

    def test_func(self):

        user = self.request.user

        return (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "rep"
        )

    def get_form(self, form_class=None):

        form = super().get_form(form_class)

        user = self.request.user

        form.fields["application"].queryset = (
            FinancingApplication.objects.filter(
                assigned_rep=user
            ).select_related(
                "customer"
            ).order_by(
                "-created_at"
            )
        )

        return form

    def get_initial(self):

        initial = super().get_initial()

        application_id = self.request.GET.get(
            "application"
        )

        if application_id:

            try:

                application = (
                    FinancingApplication.objects
                    .get(
                        pk=application_id,
                        assigned_rep=self.request.user
                    )
                )

                initial["application"] = application

            except FinancingApplication.DoesNotExist:

                pass

        return initial

    def form_valid(self, form):

        form.instance.uploaded_by = (
            self.request.user
        )

        response = super().form_valid(form)

        AuditLog.objects.create(
            user=self.request.user,
            action="Document uploaded",
            description=(
                f"Document '{self.object.title}' "
                f"was uploaded for application "
                f"'{self.object.application.application_id}'."
            )
        )

        messages.success(
            self.request,
            "Document uploaded successfully."
        )

        return response

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )

# ==========================================================
# DOCUMENT DETAIL
# ==========================================================

class DocumentDetailView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DetailView
):

    model = Document

    template_name = "documents/document_detail.html"

    context_object_name = "document"

    login_url = reverse_lazy("login")

    def get_queryset(self):

        return (
            Document.objects
            .select_related(
                "application",
                "application__customer",
                "uploaded_by",
                "reviewed_by",
            )
        )

    def test_func(self):

        user = self.request.user

        document = self.get_object()

        # ------------------------------------------
        # ADMIN
        # ------------------------------------------

        if user.is_superuser:

            return True

        # ------------------------------------------
        # REP
        # ------------------------------------------

        if (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "rep"
        ):

            return (
                document.application.assigned_rep
                == user
            )

        # ------------------------------------------
        # REVIEWER
        # ------------------------------------------

        if (
            hasattr(user, "staff_profile")
            and user.staff_profile.role == "reviewer"
        ):

            return (
                document.application.reviewer
                == user
            )

        return False

    def handle_no_permission(self):

        if not self.request.user.is_authenticated:

            return redirect("login")

        return redirect_user_to_dashboard(
            self.request.user
        )