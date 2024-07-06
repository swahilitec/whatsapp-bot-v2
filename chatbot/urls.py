# chatbot/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WhatsAppViewSet

router = DefaultRouter()
router.register(r'', WhatsAppViewSet, basename='whatsapp')

urlpatterns = [
    path('', include(router.urls)),
]
