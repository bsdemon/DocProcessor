from django.urls import path

from .api import ImportUploadApi, ImportStatusApi

urlpatterns = [
    path("imports/", ImportUploadApi.as_view()),
    path("imports/<str:uuid>/", ImportStatusApi.as_view()),
]
