from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class UserProfile(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'admin'),
        ('receptionist', 'receptionist'),
        ('doctor', 'doctor')
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = PhoneNumberField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


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
        return self.user.get_full_name()


class Service(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="services"
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} — {self.price}"


class Patient(models.Model):
    GENDER_CHOICES = (
        ("male", "male"),
        ("female", "female"),
    )

    full_name = models.CharField(max_length=255)
    phone = PhoneNumberField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.full_name


class Appointment(models.Model):
    STATUS_CHOICES = (
        ("queue", "queue"),
        ("confirmed", "confirmed"),
        ("cancelled", "cancelled"),
        ("completed", "completed")
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    registrar = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "receptionist"}
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queue")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} → {self.doctor} ({self.start_time})"


class Payment(models.Model):
    METHOD_CHOICES = (
        ("cash", "cash"),
        ("card", "card")
    )

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} ({self.method})"


class Notification(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
