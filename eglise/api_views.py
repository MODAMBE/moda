# eglise/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Publication, Message, UserProfile
from .serializers import PublicationSerializer, MessageSerializer, UserProfileSerializer

class PublicationList(APIView):
    def get(self, request):
        publications = Publication.objects.all()
        serializer = PublicationSerializer(publications, many=True)
        return Response(serializer.data)

class UserProfileDetail(APIView):
    def get(self, request, user_id):
        profile = UserProfile.objects.get(id=user_id)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

class MessagesList(APIView):
    def get(self, request, user_id):
        messages = Message.objects.filter(receiver_id=user_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
