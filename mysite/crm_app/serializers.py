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


class AdminAppointmentListSerializer(serializers.ModelSerializer):
    patient = serializers.CharField(source="patient.full_name", read_only=True)
    doctor = serializers.CharField(
        source="doctor.user.get_full_name", read_only=True
    )

    payment_method = serializers.SerializerMethodField()
    payment_amount = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = (
            "id",
            "start_time",
            "patient",
            "doctor",
            "payment_method",
            "payment_amount",
            "status",
        )

    def get_payment_method(self, obj):
        payment = obj.payments.last()
        return payment.method if payment else None

    def get_payment_amount(self, obj):
        payment = obj.payments.last()
        return payment.amount if payment else None

class AdminAddPatientSerializer(serializers.Serializer):
    # ===== PATIENT =====
    full_name = serializers.CharField()
    birth_date = serializers.DateField()
    phone = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=Patient.GENDER_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True)

    # ===== APPOINTMENT =====
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all()
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all()
    )
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all()
    )
    registrar = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.filter(role="receptionist")
    )

    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    status = serializers.ChoiceField(
        choices=Appointment.STATUS_CHOICES
    )

    def validate(self, data):
        # время
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "Время начала должно быть меньше времени окончания"
            )

        # врач ↔ отделение
        if data["doctor"].department != data["department"]:
            raise serializers.ValidationError(
                "Врач не относится к выбранному отделению"
            )

        # услуга ↔ отделение
        if data["service"].department != data["department"]:
            raise serializers.ValidationError(
                "Услуга не относится к выбранному отделению"
            )

        return data

    def create(self, validated_data):
        # 1️⃣ Patient
        patient = Patient.objects.create(
            full_name=validated_data["full_name"],
            birth_date=validated_data["birth_date"],
            phone=validated_data.get("phone"),
            gender=validated_data["gender"],
            note=validated_data.get("note", "")
        )

        # 2️⃣ Appointment
        Appointment.objects.create(
            patient=patient,
            department=validated_data["department"],
            doctor=validated_data["doctor"],
            service=validated_data["service"],
            registrar=validated_data["registrar"],
            start_time=validated_data["start_time"],
            end_time=validated_data["end_time"],
            status=validated_data["status"],
        )

        return patient

# serializers/admin_edit_appointment.py
class AdminAppointmentEditSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all()
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all()
    )
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all()
    )
    registrar = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.filter(role="receptionist")
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
        )

    def validate(self, data):
        start = data.get("start_time", self.instance.start_time)
        end = data.get("end_time", self.instance.end_time)

        if start >= end:
            raise serializers.ValidationError(
                "Время начала должно быть меньше времени окончания"
            )

        department = data.get("department", self.instance.department)
        doctor = data.get("doctor", self.instance.doctor)
        service = data.get("service", self.instance.service)

        if doctor.department != department:
            raise serializers.ValidationError(
                "Врач не относится к выбранному отделению"
            )

        if service.department != department:
            raise serializers.ValidationError(
                "Услуга не относится к выбранному отделению"
            )

        return data

class AdminPatientAppointmentHistorySerializer(serializers.ModelSerializer):
    registrar = serializers.CharField(
        source="registrar.get_full_name", read_only=True
    )
    department = serializers.CharField(
        source="department.name", read_only=True
    )
    doctor = serializers.CharField(
        source="doctor.user.get_full_name", read_only=True
    )
    service = serializers.CharField(
        source="service.name", read_only=True
    )

    status_label = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = (
            "id",
            "registrar",
            "department",
            "doctor",
            "service",
            "created_at",
            "status",
            "status_label",
        )

    def get_status_label(self, obj):
        return {
            "queue": "В ожидании",
            "confirmed": "Подтверждён",
            "completed": "Был в приёме",
            "cancelled": "Отменён",
        }.get(obj.status, obj.status)

class AdminPatientAppointmentStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    queue = serializers.IntegerField()
    completed = serializers.IntegerField()
    cancelled = serializers.IntegerField()


class AdminPatientAppointmentHistoryResponseSerializer(serializers.Serializer):
    stats = AdminPatientAppointmentStatsSerializer()
    results = AdminPatientAppointmentHistorySerializer(many=True)

class AdminPatientVisitHistorySerializer(serializers.ModelSerializer):
    registrar = serializers.CharField(
        source="registrar.get_full_name", read_only=True
    )
    department = serializers.CharField(
        source="department.name", read_only=True
    )
    doctor = serializers.CharField(
        source="doctor.user.get_full_name", read_only=True
    )
    service = serializers.CharField(
        source="service.name", read_only=True
    )

    status_label = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = (
            "id",
            "registrar",
            "department",
            "doctor",
            "service",
            "created_at",
            "status",
            "status_label",
        )

    def get_status_label(self, obj):
        return "Был в приёме"
class AdminPatientPaymentSerializer(serializers.ModelSerializer):
    department = serializers.CharField(
        source="appointment.department.name", read_only=True
    )
    doctor = serializers.CharField(
        source="appointment.doctor.user.get_full_name", read_only=True
    )
    service = serializers.CharField(
        source="appointment.service.name", read_only=True
    )

    method_label = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "department",
            "doctor",
            "service",
            "created_at",
            "method",
            "method_label",
            "amount",
        )

    def get_method_label(self, obj):
        return {
            "cash": "Наличные",
            "card": "Безналичные",
        }.get(obj.method, obj.method)

class AdminPatientDetailSerializer(serializers.ModelSerializer):
    gender_label = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id",
            "full_name",
            "phone",
            "gender",
            "gender_label",
        )

    def get_gender_label(self, obj):
        return {
            "male": "Мужской",
            "female": "Женский",
        }.get(obj.gender, obj.gender)

class AdminAppointmentPaymentCreateSerializer(serializers.Serializer):
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(),
        source="appointment"
    )
    method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        appointment = data["appointment"]

        if appointment.status == "cancelled":
            raise serializers.ValidationError(
                "Нельзя принять оплату за отменённый приём"
            )

        if appointment.payments.exists():
            raise serializers.ValidationError(
                "Оплата по этому приёму уже принята"
            )

        if data["amount"] > appointment.service.price:
            raise serializers.ValidationError(
                "Сумма не может превышать стоимость услуги"
            )

        return data

    def create(self, validated_data):
        appointment = validated_data["appointment"]

        payment = Payment.objects.create(
            appointment=appointment,
            amount=validated_data["amount"],
            method=validated_data["method"]
        )

        # ✅ админ закрывает приём
        appointment.status = "completed"
        appointment.save(update_fields=["status"])

        return payment
class AdminDoctorListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source="user.get_full_name", read_only=True
    )
    phone = serializers.CharField(
        source="user.phone", read_only=True
    )
    department = serializers.CharField(
        source="department.name", read_only=True
    )

    class Meta:
        model = Doctor
        fields = ("id","full_name","cabinet","department","phone",)

class AdminDoctorCreateUpdateSerializer(serializers.ModelSerializer):
    # данные пользователя
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Doctor
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",
            "department",
            "specialization",
            "cabinet",
            "bonus_percent",
            "photo",
        )

    def create(self, validated_data):
        user_data = {
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "email": validated_data.pop("email"),
            "phone": validated_data.pop("phone"),
            "role": "doctor",
            "username": validated_data["email"],
        }
        password = validated_data.pop("password")

        user = UserProfile.objects.create(**user_data)
        user.set_password(password)
        user.save()

        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor

    def update(self, instance, validated_data):
        user = instance.user

        for field in ["first_name", "last_name", "email", "phone"]:
            if field in validated_data:
                setattr(user, field, validated_data.pop(field))

        if "password" in validated_data:
            user.set_password(validated_data.pop("password"))

        user.save()

        return super().update(instance, validated_data)

class AdminAnalyticsSerializer(serializers.Serializer):
    growth_percent = serializers.FloatField()
    decline_percent = serializers.FloatField()
    doctors_count = serializers.IntegerField()

    total_patients = serializers.IntegerField()
    primary_percent = serializers.IntegerField()
    repeat_percent = serializers.IntegerField()

    chart = serializers.ListField()


class AdminDetailedReportRowSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    patient = serializers.CharField(
        source="appointment.patient.full_name"
    )
    service = serializers.CharField(
        source="appointment.service.name"
    )
    department = serializers.CharField(
        source="appointment.department.name"
    )
    doctor = serializers.CharField(
        source="appointment.doctor.user.get_full_name"
    )
    method_label = serializers.SerializerMethodField()
    price = serializers.DecimalField(
        source="appointment.service.price",
        max_digits=10,
        decimal_places=2
    )
    price_with_discount = serializers.SerializerMethodField()
    doctor_bonus = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "date",
            "patient",
            "department",
            "doctor",
            "service",
            "method_label",
            "price",
            "price_with_discount",
            "doctor_bonus",
        )

    # ✅ ВОТ ГЛАВНОЕ ИСПРАВЛЕНИЕ
    def get_date(self, obj):
        return obj.created_at.date().strftime("%d.%m.%Y")

    def get_method_label(self, obj):
        return "Наличные" if obj.method == "cash" else "Безналичные"

    def get_price_with_discount(self, obj):
        return obj.amount

    def get_doctor_bonus(self, obj):
        return f"{obj.appointment.doctor.bonus_percent}%"

class AdminDoctorCloseRowSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_sum = serializers.DecimalField(
        max_digits=10, decimal_places=2
    )

class AdminSummaryReportSerializer(serializers.Serializer):
    total_cash = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_card = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_sum = serializers.DecimalField(max_digits=12, decimal_places=2)

    doctors_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    doctors_cash = serializers.DecimalField(max_digits=12, decimal_places=2)
    doctors_card = serializers.DecimalField(max_digits=12, decimal_places=2)

    clinic_cash = serializers.DecimalField(max_digits=12, decimal_places=2)
    clinic_card = serializers.DecimalField(max_digits=12, decimal_places=2)

class AdminCalendarAppointmentSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    doctor = serializers.CharField(
        source="doctor.user.get_full_name", read_only=True
    )
    service = serializers.CharField(
        source="service.name", read_only=True
    )
    color = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = (
            "id",
            "start_time",
            "end_time",
            "status",
            "title",
            "doctor",
            "service",
            "color",
        )

    def get_title(self, obj):
        return f'{obj.service.name} — {obj.patient.full_name}'

    def get_color(self, obj):
        return {
            "queue": "#22c55e",       # зелёный
            "confirmed": "#3b82f6",   # синий
            "cancelled": "#ef4444",   # красный
            "completed": "#9ca3af",   # серый
        }.get(obj.status, "#9ca3af")

class AdminCalendarCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            "patient",
            "doctor",
            "department","service","start_time","end_time","status",)

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "Время начала должно быть меньше окончания"
            )
        return data

# ===== PRICE LIST (ADMIN) =====

class AdminPriceListServiceSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    class Meta:
        model = Service
        fields = ("id","name","price",)

    def get_price(self, obj):
        return f"{int(obj.price)} сом"


class AdminPriceListDepartmentSerializer(serializers.ModelSerializer):
    services = AdminPriceListServiceSerializer(many=True,read_only=True)
    class Meta:
        model = Department
        fields = ("id","name","services",)


# ===== CRUD SERVICE =====

class AdminServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("department","name","price",)

"""Receptionist"""
# ===== APPOINTMENTS LIST =====
class ReceptionistAppointmentListSerializer(serializers.ModelSerializer):
    patient = serializers.CharField(source="patient.full_name", read_only=True)
    doctor = serializers.CharField(source="doctor.user.get_full_name", read_only=True)

    payment_method = serializers.SerializerMethodField()
    payment_amount = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = (
            "id",
            "start_time",
            "patient",
            "doctor",
            "payment_method",
            "payment_amount",
            "status",
        )

    def get_payment_method(self, obj):
        payment = obj.payments.last()
        return payment.method if payment else None

    def get_payment_amount(self, obj):
        payment = obj.payments.last()
        return payment.amount if payment else None


# ===== ADD PATIENT =====
class ReceptionistAddPatientSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    birth_date = serializers.DateField()
    phone = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=Patient.GENDER_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True)

    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=Appointment.STATUS_CHOICES)

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError("Неверный интервал времени")

        if data["doctor"].department != data["department"]:
            raise serializers.ValidationError("Врач не из этого отделения")

        if data["service"].department != data["department"]:
            raise serializers.ValidationError("Услуга не из этого отделения")

        return data

    def create(self, validated_data):
        request = self.context["request"]

        patient = Patient.objects.create(
            full_name=validated_data["full_name"],
            birth_date=validated_data["birth_date"],
            phone=validated_data.get("phone"),
            gender=validated_data["gender"],
            note=validated_data.get("note", "")
        )

        Appointment.objects.create(
            patient=patient,
            department=validated_data["department"],
            doctor=validated_data["doctor"],
            service=validated_data["service"],
            registrar=request.user,
            start_time=validated_data["start_time"],
            end_time=validated_data["end_time"],
            status=validated_data["status"],
        )

        return patient


# ===== EDIT APPOINTMENT =====
class ReceptionistAppointmentEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            "id",
            "start_time",
            "end_time",
            "status",
        )


# ===== PATIENT HISTORY =====
class ReceptionistPatientAppointmentHistorySerializer(serializers.ModelSerializer):
    department = serializers.CharField(source="department.name", read_only=True)
    doctor = serializers.CharField(source="doctor.user.get_full_name", read_only=True)
    service = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "department",
            "doctor",
            "service",
            "created_at",
            "status",
        )


# ===== PAYMENTS =====
class ReceptionistPatientPaymentSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source="appointment.department.name", read_only=True)
    doctor = serializers.CharField(source="appointment.doctor.user.get_full_name", read_only=True)
    service = serializers.CharField(source="appointment.service.name", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "department",
            "doctor",
            "service",
            "created_at",
            "method",
            "amount",
        )


# ✅ ИСПРАВЛЕНО: Убрал проверку на registrar
class ReceptionistAppointmentPaymentCreateSerializer(serializers.Serializer):
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(),
        source="appointment"
    )
    method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        appointment = data["appointment"]

        # ✅ Убрали проверку: if appointment.registrar != self.context["request"].user

        if appointment.payments.exists():
            raise serializers.ValidationError("Оплата уже есть")

        return data

    def create(self, validated_data):
        request = self.context["request"]

        payment = Payment.objects.create(
            appointment=validated_data["appointment"],
            amount=validated_data["amount"],
            method=validated_data["method"],
            registrar=request.user
        )

        validated_data["appointment"].status = "completed"
        validated_data["appointment"].save(update_fields=["status"])

        return payment

# ===== RECEPTIONIST PROFILE =====
class ReceptionistProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_label = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "role_label",
        )

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_role_label(self, obj):
        return "Регистратор / ресепшнист"

# ===== RECEPTIONIST: DOCTOR LIST =====
class ReceptionistDoctorListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source="user.get_full_name", read_only=True
    )
    phone = serializers.CharField(
        source="user.phone", read_only=True
    )
    department = serializers.CharField(
        source="department.name", read_only=True
    )

    class Meta:
        model = Doctor
        fields = (
            "id",
            "full_name",
            "cabinet",
            "department",
            "phone",
        )


# ===== RECEPTIONIST: DOCTOR CREATE / UPDATE =====
class ReceptionistDoctorCreateUpdateSerializer(serializers.ModelSerializer):
    # данные пользователя
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Doctor
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",
            "department",
            "specialization",
            "cabinet",
            "bonus_percent",
            "photo",
        )

    def create(self, validated_data):
        user_data = {
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "email": validated_data.pop("email"),
            "phone": validated_data.pop("phone"),
            "role": "doctor",
            "username": validated_data["email"],
        }

        password = validated_data.pop("password")

        user = UserProfile.objects.create(**user_data)
        user.set_password(password)
        user.save()

        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor

    def update(self, instance, validated_data):
        user = instance.user

        for field in ["first_name", "last_name", "email", "phone"]:
            if field in validated_data:
                setattr(user, field, validated_data.pop(field))

        if "password" in validated_data:
            user.set_password(validated_data.pop("password"))

        user.save()
        return super().update(instance, validated_data)


class ReceptionistPriceListServiceSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ("id", "name", "price")

    def get_price(self, obj):
        return f"{int(obj.price)} сом"

class ReceptionistPriceListDepartmentSerializer(serializers.ModelSerializer):
    services = ReceptionistPriceListServiceSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Department
        fields = ("id", "name", "services")

class ReceptionistDetailedReportRowSerializer(
    AdminDetailedReportRowSerializer
):
    pass


class ReceptionistSummaryReportSerializer(
    AdminSummaryReportSerializer
):
    pass

class ReceptionistCalendarAppointmentSerializer(
    AdminCalendarAppointmentSerializer
):
    pass

class ReceptionistCalendarCreateSerializer(
    AdminCalendarCreateSerializer
):
    pass


"""Doctor"""
class DoctorCalendarSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    service = serializers.CharField(source="service.name")
    patient = serializers.CharField(source="patient.full_name")
    color = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = (
            "id",
            "start_time",
            "end_time",
            "status",
            "title",
            "service",
            "patient",
            "color",
        )

    def get_title(self, obj):
        return f"{obj.service.name} — {obj.patient.full_name}"

    def get_color(self, obj):
        return {
            "queue": "#22c55e",
            "confirmed": "#3b82f6",
            "cancelled": "#ef4444",
            "completed": "#9ca3af",
        }.get(obj.status, "#9ca3af")


class DoctorAppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ("start_time", "end_time", "status")

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError("Некорректное время")
        return data


class DoctorPatientDetailSerializer(serializers.ModelSerializer):
    gender_label = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ("id", "full_name", "phone", "gender", "gender_label", "note")

    def get_gender_label(self, obj):
        return "Мужской" if obj.gender == "male" else "Женский"

class DoctorPatientAppointmentSerializer(serializers.ModelSerializer):
    service = serializers.CharField(source="service.name")
    department = serializers.CharField(source="department.name")
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = (
            "id",
            "created_at",
            "service",
            "department",
            "status",
            "status_label",
        )

    def get_status_label(self, obj):
        return {
            "queue": "В ожидании",
            "confirmed": "Подтверждён",
            "completed": "Был в приёме",
            "cancelled": "Отменён",
        }.get(obj.status)

class DoctorPatientPaymentSerializer(serializers.ModelSerializer):
    service = serializers.CharField(source="appointment.service.name")
    method_label = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ("id", "created_at", "service", "method", "method_label", "amount")

    def get_method_label(self, obj):
        return "Наличные" if obj.method == "cash" else "Безналичные"

class DoctorProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name")
    email = serializers.EmailField(source="user.email")
    phone = serializers.CharField(source="user.phone")

    class Meta:
        model = Doctor
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "department",
            "specialization",
            "cabinet",
            "bonus_percent",
            "photo",
        )

class DoctorNotificationSerializer(serializers.ModelSerializer):
    patient = serializers.CharField(
        source="appointment.patient.full_name",
        read_only=True
    )
    department = serializers.CharField(
        source="appointment.department.name",
        read_only=True
    )
    start_time = serializers.DateTimeField(
        source="appointment.start_time",
        read_only=True
    )

    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "message",
            "patient",
            "department",
            "start_time",
            "is_read",
            "created_at",
        )