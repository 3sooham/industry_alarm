
from django.contrib import admin
from .models import Post, Comment, User

# 관리자 페이지에서 만든 모델을 보려면 admin.site.register(Post)로 모델을 등록해야 해요.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(User)