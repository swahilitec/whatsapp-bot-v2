# myproject/urls.py

from django.contrib import admin
from django.urls import path, include
from chatbot.views import webhook

urlpatterns = [
    path('admin', admin.site.urls),
    path('chatbot/', include('chatbot.urls')),
    path('webhook/', webhook, name="verify webhook"),
]