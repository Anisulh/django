from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


from ..models import Guest

from ..serializers import GuestSerializer

# URL: api/guest
# DATA: nickname
# Creates/Updates guests, specifically just the nicknames
@api_view(["POST", "PATCH", "DELETE"])
def GuestView(request, format=None):
    if request.method == "POST":
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            request.session["guest_id"] = serializer.data.get("guest_id")
            request.session.modified = True
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == "PATCH":
        try:
            guest = Guest.objects.get(pk=request.session.get("guest_id"))
        except Guest.DoesNotExist:
            return Response(
                {"error": "unable to find guest"}, status=status.HTTP_404_NOT_FOUND
            )
        update_serializer = GuestSerializer(guest, data=request.data, partial=True)
        if update_serializer.is_valid():
            update_serializer.save()
        return Response(update_serializer.data, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        try:
            guest = Guest.objects.get(pk=request.session.get("guest_id"))
        except Guest.DoesNotExist:
            return Response(
                {"error": "unable to find guest"}, status=status.HTTP_404_NOT_FOUND
            )
        guest.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
