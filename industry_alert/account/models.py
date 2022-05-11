from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.db.models.fields import related
from django.utils import timezone


class UserLinkInfo(models.Model):
    name = models.CharField(max_length=255)

# 이런거 다 eve_access_token 이렇게 바꿔야함
# myqsl에서 보기가 너무 힘듬
class EveAccessToken(models.Model):
    # fk 보다 one_to_one 사용
    # one to many보다 one to one이 조인 비용 적음
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="eve_token")
    # access_token jwt인데 이거 길이 상한이 없어서 char/varchar로 못하고 TextField로 해줘야함
    access_token = models.TextField()
    expires_in = models.DateTimeField(default=timezone.now)
    token_type = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)

# https://docs.djangoproject.com/en/3.2/ref/contrib/auth/
class AccountManager(BaseUserManager):
    def create_user(self, email, password, name):
        if not email:
            raise ValueError('Users must have an email address')


        # 이거 근데 꼭 해야하는건지는 모르겠음
        user = self.model(
            # normalize_email()이거는 @domain에서 domain만 소문자로 만듬
            email=self.normalize_email(email),
            name=name
        )

        # Sets the user’s password to the given raw string,
        # taking care of the password hashing. Doesn’t save the User object.
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, name):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            name=name
        )

        # https://docs.djangoproject.com/en/3.2/ref/contrib/auth/
        user.is_admin = True
        user.is_active = True
        user.is_superuser = True
        user.save()

# drf login
# https://medium.com/geekculture/register-login-and-logout-users-in-django-rest-framework-51486390c29
# https://github.com/django/django/blob/910ecd1b8df7678f45c3d507dde6bcb1faafa243/django/contrib/auth/base_user.py#L16 참조하기
# 여기에 이름 생년월일 전화번호 같은 거 더 추가하기


# 여기에다가 eve esi account id 추가해야함 그래야지 그거가지고 esi request함
# model methods는 row에 해당하는 것만 넣어주고 manager methods는 테이블 전체에 적용되는 것을 적는게 좋음
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True, default=None)
    password = models.CharField(verbose_name='password', max_length=255)
    # charfield는 null true하는거아님 값이 비어있다를 표시하는게 빈스트링이랑 null 두가지가 다되면서 곱창남
    name = models.CharField(verbose_name='name', max_length=30, default='', blank=True)
    character_id = models.IntegerField(verbose_name='character_id', default=0, blank=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    link_info = models.ForeignKey(UserLinkInfo, related_name='users', on_delete=models.SET_NULLL, null=True)

    # username으로 'email' field 사용함
    USERNAME_FIELD = 'email'

    # superuser 생성시 추가로 받을거
    # https://docs.djangoproject.com/en/3.2/topics/auth/customizing/
    REQUIRED_FIELDS = ['name']

    objects = AccountManager()

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return str(self.email)