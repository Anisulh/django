from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Room, Guest
from ..serializers import CreateRoomSerializer, RoomSerializer


# URL: api/room
# Creates room
# DATA: name, host_id, guest_controller
@api_view(["POST"])
def RoomView(request, format=None):
    if request.method == "POST":
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            host_id = serializer.validated_data.get("host_id")
            try:
                Guest.objects.get(guest_id=host_id)
            except Guest.DoesNotExist:
                return Response(
                    {"error": "guest not found"}, status=status.HTTP_404_NOT_FOUND
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


# URL: api/room/<str:room_code>
# DATA: room_code, guest_id
# Gets/Updates info of a specific room using room_code
@api_view(["GET", "PATCH", "POST", "DELETE"])
def SpecificRoomView(request, room_code, format=None):
    try:
        room = Room.objects.get(pk=room_code)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # GET specific room
    if request.method == "GET":
        serializer = RoomSerializer(instance=room, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update specific room
    if request.method == "PATCH":
        guest_id = request.data.get("guest_id")
        if guest_id != room.host_id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = RoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # join room
    if request.method == "POST":
        guest_id = request.data.get("guest_id")
        serializer = RoomSerializer(instance=room, many=False)
        try:
            guest = Guest.objects.get(pk=guest_id)
        except Guest.DoesNotExist:
            return Response(
                {"error": "guest not found"}, status=status.HTTP_404_NOT_FOUND
            )
        room.join(guest)
        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    # delete room
    if request.method == "DELETE":
        guest_id = request.data.get("guest_id")
        try:
            query_guest = Guest.objects.get(pk=guest_id)
        except:
            return Response(
                {"error": "guest not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if room.host_id == guest_id:
            room.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            room.leave(query_guest)
            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
    return Response({"error": "something went wrong"}, status=status.HTTP_404_NOT_FOUND)
