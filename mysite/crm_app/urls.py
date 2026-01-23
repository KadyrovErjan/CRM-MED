from django.urls import path, include
from .views import *

urlpatterns = [
    path("doctors/", DoctorListCreateView.as_view()),

    path("patients/", PatientListCreateView.as_view()),
    path("appointments/", AppointmentListCreateView.as_view()),
    path("payments/", PaymentCreateView.as_view()),

    path("doctor/appointments/", DoctorAppointmentsView.as_view()),
    path("notifications/", NotificationListView.as_view()),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='login'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),

    # USERS
    path("admin_role/users/create/", AdminUserCreateView.as_view()),

    # DEPARTMENTS
    path("admin_role/departments/", DepartmentListCreateView.as_view()),
    path("admin_role/departments/<int:pk>/", DepartmentDetailView.as_view()),

    # DOCTORS
    path("admin_role/doctors/", DoctorListCreateView.as_view()),
    path("admin_role/doctors/<int:pk>/", DoctorDetailView.as_view()),

    # PRICE LIST
    path("admin_role/services/", ServiceListCreateView.as_view()),
    path("admin_role/services/<int:pk>/", ServiceDetailView.as_view()),

    # PATIENTS
    path("admin_role/patients/", PatientAdminListView.as_view()),

    # APPOINTMENTS (TABLE + CALENDAR)
    path("admin_role/appointments/", AppointmentAdminListView.as_view()),

    # PAYMENTS / ANALYTICS
    path("admin_role/payments/", PaymentAdminListView.as_view()),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register("patients", PatientViewSet)
router.register("appointments", AppointmentViewSet)
router.register("payments", PaymentViewSet)
router.register("doctors", DoctorListViewSet)
router.register("services", ServiceViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("analytics/", ReceptionistAnalyticsView.as_view()),
]

