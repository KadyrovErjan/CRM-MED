import django_filters
from .models import Appointment


class AppointmentFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="start_time", lookup_expr="date__gte")
    date_to = django_filters.DateFilter(field_name="start_time", lookup_expr="date__lte")

    class Meta:
        model = Appointment
        fields = ["doctor", "department", "status"]
