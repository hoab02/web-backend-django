from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests  # Sử dụng để gọi đến khối xử lý dữ liệu


# Create your views here.

# Gọi đến khối xử lý dữ liệu để điều khiển robot di chuyển
@api_view(['POST'])
def move_robot(request):
    data = request.data
    print("DATA MOVE RECEIVE", data)
    # Giả sử URL của khối xử lý dữ liệu là http://localhost:5000/move
    try:
        response = requests.post('http://localhost:3003/move', json=data)
        if response.status_code == 200:
            return Response({"message": "Robot moved successfully"}, status=200)
        else:
            return Response({"error": "Failed to move robot"}, status=response.status_code)
    
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=500)

# Gọi đến khối xử lý dữ liệu để xoay robot
@api_view(['POST'])
def rotate_robot(request):
    data = request.data
    print("DATA ROTATE RECEIVE", data)
    # Giả sử URL của khối xử lý dữ liệu là http://localhost:5000/rotate
    try:
        response = requests.post('http://localhost:3003/rotate', json=data)
        if response.status_code == 200:
            return Response({"message": "Robot rotated successfully"}, status=200)
        else:
            return Response({"error": "Failed to rotate robot"}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=500)
