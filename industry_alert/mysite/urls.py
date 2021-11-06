"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.contrib.auth import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # 이거 127.0.0.1:8000하면 127.0.0.1:8000/accounts/login/ 가는 이유
    # 1. path('', include('blog.urls')),
    # 2. path('', views.post_list, name='post_list'),
    # 3. post_list 뷰 실행하려 했는데 login_required 데코레이터 붙어있으니까 로그인 페이지로 가는거임
    # 근데 이제 어디가 로그인 페이지인지 아는거냐?
    # https://github.com/django/django/blob/00ea883ef56fb5e092cbe4a6f7ff2e7470886ac4/django/contrib/auth/decorators.py#L38
    # login_required 데코레이터를 보면
    # https://github.com/django/django/blob/00ea883ef56fb5e092cbe4a6f7ff2e7470886ac4/django/contrib/auth/decorators.py#L23
    # resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
    # 인자에 login_url없으면 settings에 정의된 LOGIN_URL가져옴
    # 그 세팅은 https://github.com/django/django/blob/1783b3cb24cdefd8e1e3d73acd1d1ef3011c96be/django/conf/global_settings.py
    # global_settings.py 말하는거임
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    # 로그아웃하면 '/'로 이동함
    path('accounts/logout/', views.LogoutView.as_view(next_page = '/'), name='logout'),
    # next_page가 들어가면 
    # 지금 상태는 로그아웃하면 setting.py에 LOGOUT_REDIRECT_URL = '/' 이거로 가도록 해둠
    # path('accounts/logout/', views.LogoutView.as_view(), name='logout'),
    # 장고는 http://127.0.0.1:8000/ 로 들어오는 모든 접속 요청을 blog.urls로 전송해 추가 명령을 찾을 거예요.
    path('', include('blog.urls')),
    path('', include('account.urls')),
]