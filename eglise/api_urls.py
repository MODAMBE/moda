# eglise/api_urls.py
from django.urls import path
from .api_views import PublicationList, UserProfileDetail, MessagesList

urlpatterns = [
    path('publications/', PublicationList.as_view(), name='api_publications'),
    path('profile/<int:user_id>/', UserProfileDetail.as_view(), name='api_profile'),
    path('messages/<int:user_id>/', MessagesList.as_view(), name='api_messages'),
]
