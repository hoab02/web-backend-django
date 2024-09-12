from django.shortcuts import render, redirect
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Robot, MapCheck, MapQuery, RobotRegister
from .serializers import RobotSerializer, RobotRegisterSerializer
from .forms import JSONFileForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import zipfile
import json
import requests

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def update_robot(request, robot_id):
    try:
        robot = Robot.objects.get(robotID=robot_id)
    except Robot.DoesNotExist:
        return Response({'error': 'Robot not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = RobotSerializer(robot, data=request.data, partial=True)  # partial=True để cho phép cập nhật một phần
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
class RobotViewSet(viewsets.ModelViewSet):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer
    
class RobotRegistrationView(APIView):
    def post(self, request):
        serializer = RobotRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RobotRegistrationView(APIView):
    def post(self, request):
        data = request.data
        
        device_info = data.get('Body', {}).get('Device', {})
        serial_no = device_info.get('SerialNo')

        # Check if the device already exists in the database
        if RobotRegister.objects.filter(device=serial_no).exists():
            robot = get_object_or_404(RobotRegister, device=serial_no)
            robot.state = 'inactive'
            robot.save()
            return Response({"message": "Device already registered"}, status=status.HTTP_200_OK)

        # Chuẩn bị dữ liệu cho model Robot
        robot_data = {
            "device": device_info.get('SerialNo'),
            "ip": device_info.get('Ip'),
            "port": device_info.get('Port'),
            "type": device_info.get('DeviceType'),
            "state": 'inactive'  # Hoặc bất kỳ trạng thái mặc định nào
        }

        serializer = RobotRegisterSerializer(data=robot_data)
        if serializer.is_valid():
            serializer.save()
            # Xử lý để cho phép đăng nhập, có thể là tạo token hoặc trả về thông tin xác thực
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RobotRegistrationListView(APIView):
    def get(self, request):
        robots = RobotRegister.objects.all()
        serializer = RobotRegisterSerializer(robots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class MapUploadAndAPI(APIView):

    def get(self, request, map_name=None):
        # Nếu có map_name, trả về dữ liệu MapCheck qua API
        if map_name:
            try:
                map_check_instance = MapCheck.objects.get(map_name=map_name)
                return JsonResponse(map_check_instance.data, safe=False)
            except MapCheck.DoesNotExist:
                return JsonResponse({"error": "MapCheck not found"}, status=404)
        # Nếu không có map_name, hiển thị form upload
        form = JSONFileForm()
        return render(request, 'robots/upload_zip.html', {'form': form})

    def post(self, request):
        # Xử lý file ZIP được upload
        form = JSONFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                # Extract và xử lý file topo.json
                with zip_ref.open('topo.json') as f:
                    topo_data = json.load(f)
                    map_data = self.extract_fields(topo_data)

                    # Lưu dữ liệu vào MapCheck
                    map_check_instance, created = MapCheck.objects.update_or_create(
                        map_name = map_data.get('name', 'unknown'),
                        defaults = {'data': map_data}
                    )

                    # Xóa các node cũ trong MapQuery liên quan đến MapCheck này
                    MapQuery.objects.filter(map_check=map_check_instance).delete()

                    # Lưu các nodes mới vào MapQuery
                    for node in map_data.get('nodes', []):
                        MapQuery.objects.create(
                            node_id=node.get('id'),
                            edges=node.get('edges'),
                            type=node.get('type'),
                            coordinate_x=node['coordinate']['x'],
                            coordinate_y=node['coordinate']['y'],
                            map_check=map_check_instance  # Liên kết với MapCheck hiện tại
                        )

            return redirect(request.META.get('HTTP_REFERER', '/'))  # Chuyển hướng sau khi upload thành công
        return render(request, 'robots/upload_zip.html', {'form': form})

    def extract_fields(self, data):

        extracted_data = {
            'name': data.get('map', {}).get('name'),
            'width': data.get('map', {}).get('width'),
            'height': data.get('map', {}).get('height'),
            'nodes': []
        }

        for node in data.get('nodes', []):
            extracted_node = {
                'id': node.get('id'),
                'edges': node.get('edges'),
                'type': node.get('type'),
                'coordinate': node.get('coordinate')
            }
            extracted_data['nodes'].append(extracted_node)

        return extracted_data


@api_view(['POST'])
def register_robot(request):
    data = request.data
    device_serial = data.get('Device')

    print("DATA REG RECEIVE", data)

    if not device_serial:
        return Response({"error": "Device Serial Number not provided"}, status=400)

    try:
        # Call the external service to activate the robot login
        response = requests.post('http://127.0.0.1:3003/activate_robot_login', json=data)
        
        if response.status_code == 200:
            # Find the robot in the database by its serial number (device)
            robot = get_object_or_404(RobotRegister, device=device_serial)
            
            # Update the robot's state to 'active'
            robot.state = 'active'
            robot.save()

            return Response({"message": "Robot registered and activated successfully"}, status=200)
        else:
            return Response({"error": "Failed to register robot"}, status=response.status_code)

    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=500)
