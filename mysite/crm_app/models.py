from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from datetime import date
from django.core.exceptions import ValidationError


# =========================
# USER
# =========================
class UserProfile(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('receptionist', 'Receptionist'),
        ('doctor', 'Doctor')
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = PhoneNumberField(null=True, blank=True)

    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.email


# =========================
# DEPARTMENT
# =========================
class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# =========================
# DOCTOR
# =========================
class Doctor(models.Model):
    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "doctor"}
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="doctors"
    )
    specialization = models.CharField(max_length=255)
    cabinet = models.CharField(max_length=15)
    bonus_percent = models.PositiveIntegerField(default=0)
    photo = models.ImageField(upload_to="doctors/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.cabinet} кабинет"


# =========================
# SERVICE
# =========================
class Service(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="services"
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} — {int(self.price)} c"


# =========================
# PATIENT
# =========================
class Patient(models.Model):
    GENDER_CHOICES = (
        ("male", "male"),
        ("female", "female"),
    )

    full_name = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    phone = PhoneNumberField(null=True, blank=True, db_index=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


# =========================
# APPOINTMENT
# =========================
class Appointment(models.Model):
    STATUS_CHOICES = (
        ("queue", "queue"),
        ("confirmed", "confirmed"),
        ("cancelled", "cancelled"),
        ("completed", "completed")
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )
    registrar = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "receptionist"}
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="queue"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} → {self.doctor} ({self.start_time})"

    def clean(self):
        if self.doctor.department != self.department:
            raise ValidationError("Врач не относится к выбранному отделению")

        if self.service.department != self.department:
            raise ValidationError("Услуга не относится к выбранному отделению")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# =========================
# PAYMENT
# =========================
class Payment(models.Model):
    METHOD_CHOICES = (
        ("cash", "Наличные"),
        ("card", "Карта")
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    registrar = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "receptionist"}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{int(self.amount)} c ({self.method})"


# =========================
# NOTIFICATION
# =========================
# models.py
class Notification(models.Model):
    recipient = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
