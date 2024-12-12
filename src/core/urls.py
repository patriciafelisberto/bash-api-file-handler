from django.urls import path, include

from rest_framework.routers import DefaultRouter

from core.views import (
    UploadFileViewSet,
    ListFilesViewSet,
    MaxMinSizeViewSet,
    OrderByUsernameViewSet,
    BetweenMsgsViewSet,
)

router = DefaultRouter()
router.register(r'upload-file', UploadFileViewSet, basename='upload-file')
router.register(r'list-files', ListFilesViewSet, basename='list-files')
router.register(r'max-min-size', MaxMinSizeViewSet, basename='max-min-size')
router.register(r'order-by-username', OrderByUsernameViewSet, basename='order-by-username')
router.register(r'between-msgs', BetweenMsgsViewSet, basename='between-msgs')

urlpatterns = [
    path('', include(router.urls)),
]
