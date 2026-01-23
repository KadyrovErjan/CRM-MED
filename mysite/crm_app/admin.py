from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(Service)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Payment)
admin.site.register(Notification)