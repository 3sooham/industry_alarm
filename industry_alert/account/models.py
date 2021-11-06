from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin


# https://docs.djangoproject.com/en/3.2/ref/contrib/auth/
class AccountManager(BaseUserManager):
    def create_user(self, email, password, name):
        if not email:
            raise ValueError('Users must have an email address')
        print('어카운트')
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
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True, default=None)
    password = models.CharField(verbose_name='password', max_length=255)
    # charfield는 null true하는거아님 값이 비어있다를 표시하는게 빈스트링이랑 null 두가지가 다되면서 곱창남
    name = models.CharField(verbose_name='name', max_length=30, default='', blank=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

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