
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PokerDataViewSet

router = DefaultRouter()
router.register(r'poker-data', PokerDataViewSet, basename='poker-data')

urlpatterns = [
    path('', include(router.urls)),
]