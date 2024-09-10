from django.urls import path
from . import views

urlpatterns = [
    path('move/', views.move_robot, name='move_robot'),
    path('rotate/', views.rotate_robot, name='rotate_robot'),
]
