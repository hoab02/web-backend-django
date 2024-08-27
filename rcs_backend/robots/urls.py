from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RobotViewSet, MapUploadAndAPI

router = DefaultRouter()
router.register(r'robots', RobotViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', MapUploadAndAPI.as_view(), name='upload_zip'),
    path('api/mapcheck/<str:map_name>/', MapUploadAndAPI.as_view(), name='get_map_check'),
]
