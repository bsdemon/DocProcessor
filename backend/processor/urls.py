from django.urls import path

from .api import ImportUploadApi, ImportStatusApi

urlpatterns = [
    path("imports/", ImportUploadApi.as_view()),
    path("imports/<str:pk>/", ImportStatusApi.as_view()),
]
