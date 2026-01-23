from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django_rest_passwordreset.models import ResetPasswordToken



User = get_user_model()

class CustomLoginSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        role = data.get("role")
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": "Пользователь с таким email не найден"
            })

        # 🔒 ПРОВЕРКА РОЛИ
        if user.role != role:
            raise serializers.ValidationError({
                "role": "Роль не соответствует пользователю"
            })

        # 🔒 ПРОВЕРКА ПАРОЛЯ
        if not user.check_password(password):
            raise serializers.ValidationError({
                "password": "Неверный пароль"
            })

        if not user.is_active:
            raise serializers.ValidationError(
                "Пользователь не активен"
            )

        self.context["user"] = user
        return data

    def to_representation(self, instance):
        user = self.context["user"]
        refresh = RefreshToken.for_user(user)

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "full_name": user.get_full_name(),
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get('refresh')
        try:
            RefreshToken(token)
        except Exception:
            raise serializers.ValidationError({"refresh": "Невалидный токен"})
        return attrs


class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_code = serializers.IntegerField()
    new_password = serializers.CharField(write_only=True, min_length=4)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        reset_code = data.get('reset_code')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("Пароли не совпадают.")

        try:
            token = ResetPasswordToken.objects.get(user__email=email, key=str(reset_code))
        except ResetPasswordToken.DoesNotExist:
            raise serializers.ValidationError("Неверный код сброса или email.")

        data['user'] = token.user
        data['token'] = token
        return data

    def save(self):
        user = self.validated_data['user']
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        # Удаляем использованный токен
        token.delete()

# ===== USERS (create doctor / receptionist) =====
class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "role",
            "first_name",
            "last_name",
            "phone",
        )

    def validate_role(self, value):
        if value not in ["doctor", "receptionist"]:
            raise serializers.ValidationError(
                "Admin может создавать только doctor или receptionist"
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.username = user.email
        user.set_password(password)
        user.save()
        return user


# ===== DEPARTMENT =====
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


# ===== DOCTOR =====
class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source="user.get_full_name", read_only=True
    )
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Doctor
        fields = (
            "id",
            "user",
            "full_name",
            "email",
            "phone",
            "department",
            "specialization",
            "cabinet",
            "bonus_percent",
            "photo",
        )


# ===== SERVICE / PRICE LIST =====
class ServiceSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name", read_only=True
    )

    class Meta:
        model = Service
        fields = "__all__"


# ===== PATIENT (ADMIN VIEW ONLY) =====
class PatientAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


# ===== APPOINTMENTS (ADMIN TABLE + CALENDAR) =====
class AppointmentAdminSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    doctor_name = serializers.CharField(
        source="doctor.user.get_full_name", read_only=True
    )
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = Appointment
        fields = "__all__"


# ===== PAYMENTS / ANALYTICS =====
class PaymentAdminSerializer(serializers.ModelSerializer):
    patient = serializers.CharField(
        source="appointment.patient.full_name", read_only=True
    )
    doctor = serializers.CharField(
        source="appointment.doctor.user.get_full_name", read_only=True
    )
    service = serializers.CharField(
        source="appointment.service.name", read_only=True
    )

    class Meta:
        model = Payment
        fields = "__all__"



class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ("registrar",)

    def create(self, validated_data):
        validated_data["registrar"] = self.context["request"].user
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("user",)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

class ReceptionPatientListSerializer(serializers.ModelSerializer):
    appointments_count = serializers.IntegerField(
        source="appointments.count", read_only=True
    )

    class Meta:
        model = Patient
        fields = (
            "id",
            "full_name",
            "phone",
            "gender",
            "appointments_count",
        )

class ReceptionPatientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            "id",
            "full_name",
            "phone",
            "gender",
            "note",
        )


class ReceptionPatientAppointmentHistorySerializer(serializers.ModelSerializer):
    department = serializers.CharField(source="department.name", read_only=True)
    doctor = serializers.CharField(
        source="doctor.user.get_full_name", read_only=True
    )
    service = serializers.CharField(source="service.name", read_only=True)
    registrar = serializers.CharField(
        source="registrar.get_full_name", read_only=True
    )

    class Meta:
        model = Appointment
        fields = (
            "id",
            "department",
            "doctor",
            "service",
            "registrar",
            "start_time",
            "end_time",
            "status",
            "created_at",
        )

class ReceptionCalendarSerializer(serializers.ModelSerializer):
    patient = serializers.CharField(source="patient.full_name", read_only=True)
    doctor = serializers.CharField(
        source="doctor.user.get_full_name", read_only=True
    )
    service = serializers.CharField(source="service.name", read_only=True)

    color = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient",
            "doctor",
            "service",
            "start_time",
            "end_time",
            "status",
            "color",
        )

    def get_color(self, obj):
        return {
            "queue": "green",
            "confirmed": "blue",
            "cancelled": "red",
            "completed": "gray",
        }.get(obj.status, "gray")
