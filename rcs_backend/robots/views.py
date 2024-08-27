from django.shortcuts import render, redirect
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Robot, MapCheck, MapQuery
from .serializers import RobotSerializer
from .forms import JSONFileForm
from django.http import JsonResponse
import zipfile
import json


# Create your views here.
class RobotViewSet(viewsets.ModelViewSet):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer
    
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
                    # print("$$$$$$$", topo_data)
                
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

    

