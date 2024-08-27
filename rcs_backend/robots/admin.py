from django.contrib import admin

# Register your models here.
# robots/admin.py
from .models import Robot

admin.site.register(Robot)
