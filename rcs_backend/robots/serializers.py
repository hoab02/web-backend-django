from rest_framework import serializers
from .models import Robot, RobotRegister

class RobotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Robot
        fields = '__all__'
        
class RobotRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RobotRegister
        fields = ['device', 'ip', 'port', 'type', 'state']
