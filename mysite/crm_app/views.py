from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import *
from .permissions import *
from .filters import AppointmentFilter
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import VerifyResetCodeSerializer



class CustomLoginView(generics.GenericAPIView):
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'detail': 'Невалидный токен'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_reset_code(request):
    serializer = VerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Пароль успешно сброшен.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===== USERS =====
class AdminUserCreateView(generics.CreateAPIView):
    serializer_class = AdminUserCreateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# ===== DEPARTMENTS =====
class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# ===== DOCTORS =====
class DoctorListCreateView(generics.ListCreateAPIView):
    queryset = Doctor.objects.select_related("user", "department")
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.select_related("user", "department")
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# ===== PRICE LIST =====
class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.select_related("department")
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.select_related("department")
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# ===== PATIENTS (ADMIN VIEW) =====
class PatientAdminListView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientAdminSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# ===== APPOINTMENTS (TABLE + CALENDAR) =====
class AppointmentAdminListView(generics.ListAPIView):
    queryset = Appointment.objects.select_related(
        "patient", "doctor", "service", "department"
    )
    serializer_class = AppointmentAdminSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "doctor",
        "department",
        "status",
        "start_time",
    ]


# ===== PAYMENTS / ANALYTICS =====
class PaymentAdminListView(generics.ListAPIView):
    queryset = Payment.objects.select_related(
        "appointment",
        "appointment__patient",
        "appointment__doctor",
    )
    serializer_class = PaymentAdminSerializer
    permission_classes = [IsAuthenticated, IsAdmin]



# ===== RECEPTIONIST =====

class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsReceptionist]


class AppointmentListCreateView(generics.ListCreateAPIView):
    queryset = Appointment.objects.all().select_related("doctor", "patient")
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsReceptionist]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AppointmentFilter


class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsReceptionist]


# ===== DOCTOR =====

class DoctorAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        return Appointment.objects.filter(doctor__user=self.request.user)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

from django.db.models import Sum


class ReceptionistAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsReceptionist]

    def get(self, request):
        payments = Payment.objects.all()

        cash = payments.filter(method="cash").aggregate(total=Sum("amount"))["total"] or 0
        card = payments.filter(method="card").aggregate(total=Sum("amount"))["total"] or 0

        return Response({
            "cash_total": cash,
            "card_total": card,
            "overall": cash + card
        })
