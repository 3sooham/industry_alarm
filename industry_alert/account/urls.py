from django.urls import path
from django.urls import include # re_path용
#  blog 애플리케이션에서 사용할 모든 views를 가져왔어요
from . import views

# drf
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'user', views.AccountViewSet, basename='logins')
router.register(r'evelogin', views.EveLoginViewSet, basename='evelogins')

urlpatterns = [
    path('', include(router.urls)),
]
