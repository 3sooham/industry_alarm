from django.urls import path
from django.urls import include

from . import views

# drf
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'eve', views.EveViewSet, basename='eve')

urlpatterns = [
    # drf
    path('', include(router.urls)),
]