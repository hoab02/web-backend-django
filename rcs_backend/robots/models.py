from django.contrib.postgres.fields import ArrayField
from django.db import models
import json

class Robot(models.Model):
    robotID = models.CharField(max_length=100, unique=True)
    battery = models.FloatField()
    last2Dcode = models.CharField(max_length=100)
    mapID = models.CharField(max_length=100)
    orientation = models.FloatField()
    payload = models.FloatField()
    position = ArrayField(models.FloatField(), size=2)  # Mảng 2 giá trị, lưu vị trí X, Y
    speed = models.FloatField()
    state = models.CharField(max_length=50)
    taskID = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.robotID

class MapCheck(models.Model):
    map_name = models.CharField(max_length=255)
    data = models.JSONField()  # Lưu file JSON đã xử lý

    def __str__(self):
        return self.map_name

class MapQuery(models.Model):
    node_id = models.CharField(max_length=255)
    edges = models.JSONField()  # JSON chứa thông tin về edges
    type = models.IntegerField()  # Loại của node, lưu trữ dưới dạng số nguyên
    coordinate_x = models.FloatField()  # Tọa độ X của node
    coordinate_y = models.FloatField()  # Tọa độ Y của node
    map_check = models.ForeignKey(MapCheck, on_delete=models.CASCADE)  # Liên kết với MapCheck

    def __str__(self):
        return self.node_id

class RobotRegister(models.Model):
    device = models.CharField(max_length=100)
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    type = models.CharField(max_length=50)
    state = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive')])

    def __str__(self):
        return f"{self.device} ({self.ip}:{self.port})"
