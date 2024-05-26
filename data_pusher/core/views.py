from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
import requests

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

@api_view(['POST'])
def incoming_data(request):
    token = request.headers.get('CL-X-TOKEN')
    if not token:
        return Response({"message": "Un Authenticate"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        account = Account.objects.get(app_secret_token=token)
    except Account.DoesNotExist:
        return Response({"message": "Un Authenticate"}, status=status.HTTP_401_UNAUTHORIZED)

    data = request.data

    for destination in account.destinations.all():
        headers = destination.headers
        url = destination.url
        method = destination.http_method.upper()

        if method == 'GET':
            response = requests.get(url, headers=headers, params=data)
        else:
            response = requests.request(method, url, headers=headers, json=data)

        if response.status_code != 200:
            return Response({"message": f"Failed to send data to {url}"}, status=response.status_code)

    return Response({"message": "Data sent successfully"})
