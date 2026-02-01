from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='login'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),

    #Admin
    path("admin_role/users/create/", AdminUserCreateView.as_view()),
    path("admin_role/appointments/", AdminAppointmentListAPIView.as_view(),name="admin-appointments-list"),
    path("admin_role/patients/add/",AdminAddPatientAPIView.as_view(),name="admin-add-patient"),
    path("admin_role/appointments/<int:pk>/edit/", AdminAppointmentEditAPIView.as_view(), name="admin-appointment-edit"),
    path("admin_role/patients/<int:patient_id>/appointments/",AdminPatientAppointmentHistoryAPIView.as_view(),name="admin-patient-appointment-history"),
    path("admin_role/appointments/<int:pk>/delete/",AdminAppointmentDeleteAPIView.as_view(),name="admin-appointment-delete"),
    path("admin_role/patients/<int:patient_id>/visits/",AdminPatientVisitHistoryAPIView.as_view(),name="admin-patient-visit-history"),
    path("admin_role/patients/<int:patient_id>/payments/", AdminPatientPaymentAPIView.as_view(),name="admin-patient-payments"),
    path("admin_role/patients/<int:id>/",AdminPatientDetailAPIView.as_view(),name="admin-patient-detail"),
    path("admin_role/appointments/payment/",AdminAppointmentPaymentCreateAPIView.as_view(),name="admin-appointment-payment"),
    path("admin_role/doctors/",AdminDoctorListAPIView.as_view(),name="admin-doctor-list"),
    path("admin_role/doctors/create/",AdminDoctorCreateAPIView.as_view(),name="admin-doctor-create"),
    path("admin_role/doctors/<int:pk>/",AdminDoctorDetailAPIView.as_view(),name="admin-doctor-detail"),
    path("admin_role/analytics/",AdminAnalyticsAPIView.as_view(),name="admin-analytics"),
    path("admin_role/reports/detailed/",AdminDetailedReportAPIView.as_view(),name="admin-detailed-report"),
    path("admin_role/reports/detailed/excel/",AdminDetailedReportExcelAPIView.as_view(),name="admin-detailed-report-excel"),
    path("admin_role/reports/doctors-close/",AdminDoctorCloseReportAPIView.as_view(),name="admin-doctor-close-report"),
    path("admin_role/reports/doctors-close/excel/",AdminDoctorCloseReportExcelAPIView.as_view(),name="admin-doctor-close-report-excel"),
    path("admin_role/reports/summary/",AdminSummaryReportAPIView.as_view(),name="admin-summary-report"),
    path("admin_role/reports/summary/excel/",AdminSummaryReportExcelAPIView.as_view(),name="admin-summary-report-excel"),
    path("admin_role/calendar/",AdminCalendarListAPIView.as_view(),name="admin-calendar"),
    path("admin_role/calendar/create/",AdminCalendarCreateAPIView.as_view(),name="admin-calendar-create"),
    path("admin_role/calendar/<int:pk>/update/",AdminCalendarUpdateAPIView.as_view(),name="admin-calendar-update"),
    path("admin_role/calendar/<int:pk>/delete/",AdminCalendarDeleteAPIView.as_view(),name="admin-calendar-delete"),
    path("admin_role/price-list/",AdminPriceListAPIView.as_view(),name="admin-price-list"),
    path("admin_role/services/create/",AdminServiceCreateAPIView.as_view(),name="admin-service-create"),
    path("admin_role/services/<int:pk>/update/",AdminServiceUpdateAPIView.as_view(),name="admin-service-update"),
    path("admin_role/services/<int:pk>/delete/",AdminServiceDeleteAPIView.as_view(),name="admin-service-delete"),

    #Resipshionist
    path("receptionist_role/appointments/",ReceptionistAppointmentListAPIView.as_view(),name="receptionist-appointments"),
    path("receptionist_role/patients/add/",ReceptionistAddPatientAPIView.as_view(),name="receptionist-add-patient"),
    path("receptionist_role/appointments/<int:pk>/edit/",ReceptionistAppointmentEditAPIView.as_view(),name="receptionist-appointment-edit"),
    path("receptionist_role/patients/<int:patient_id>/appointments/",ReceptionistPatientAppointmentHistoryAPIView.as_view(),name="receptionist-patient-appointments"),
    path("receptionist_role/patients/<int:patient_id>/payments/",ReceptionistPatientPaymentAPIView.as_view(),name="receptionist-patient-payments"),
    path("receptionist_role/appointments/payment/",ReceptionistAppointmentPaymentCreateAPIView.as_view(),name="receptionist-appointment-payment"),
    path("receptionist_role/profile/",ReceptionistProfileAPIView.as_view(),name="receptionist-profile"),
    path("receptionist_role/doctors/",ReceptionistDoctorListAPIView.as_view(),name="receptionist-doctor-list",),
    path("receptionist_role/doctors/create/",ReceptionistDoctorCreateAPIView.as_view(),name="receptionist-doctor-create",),
    path("receptionist_role/doctors/<int:pk>/",ReceptionistDoctorDetailAPIView.as_view(),name="receptionist-doctor-detail",),
    path("receptionist_role/doctors/",ReceptionistDoctorListAPIView.as_view()),
    path("receptionist_role/doctors/create/",ReceptionistDoctorCreateAPIView.as_view()),
    path("receptionist_role/doctors/<int:pk>/",ReceptionistDoctorDetailAPIView.as_view()),
    path("receptionist_role/price-list/",ReceptionistPriceListAPIView.as_view()),
    path("receptionist_role/reports/detailed/",ReceptionistDetailedReportAPIView.as_view()),
    path("receptionist_role/reports/summary/",ReceptionistSummaryReportAPIView.as_view()),
    path("receptionist_role/calendar/",ReceptionistCalendarListAPIView.as_view()),
    path("receptionist_role/calendar/create/",ReceptionistCalendarCreateAPIView.as_view()),
    path("receptionist_role/calendar/<int:pk>/update/",ReceptionistCalendarUpdateAPIView.as_view()),
    path("receptionist_role/calendar/<int:pk>/delete/",ReceptionistCalendarDeleteAPIView.as_view()),
# Doctor role
    # Doctor
    path("doctor_role/calendar/", DoctorCalendarAPIView.as_view()),
    path("doctor_role/appointments/<int:pk>/update/", DoctorAppointmentUpdateAPIView.as_view()),
    path("doctor_role/profile/", DoctorProfileAPIView.as_view()),
    path("doctor_role/patients/<int:pk>/", DoctorPatientDetailAPIView.as_view()),
    path("doctor_role/patients/<int:patient_id>/appointments/", DoctorPatientAppointmentsAPIView.as_view()),
    path("doctor_role/patients/<int:patient_id>/payments/", DoctorPatientPaymentsAPIView.as_view()),

# Doctor notifications
    path("doctor_role/notifications/",DoctorNotificationListAPIView.as_view(),name="doctor-notifications"),
    path("doctor_role/notifications/<int:pk>/read/",DoctorNotificationReadAPIView.as_view(),name="doctor-notification-read"),

]