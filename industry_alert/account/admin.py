from django.contrib import admin
from .models import EveAccessToken

# ModelAdmin class를 define하지 않으면 default admin interface가 제공됨
admin.site.register(EveAccessToken)
