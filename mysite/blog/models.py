from django.conf import settings
from django.db import models
from django.utils import timezone

# drf login
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

class Post(models.Model):
    # models.ForeignKey - 다른 모델에 대한 링크를 의미합니다.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # models.CharField - 글자 수가 제한된 텍스트를 정의할 때 사용합니다. 글 제목같이 짧은 문자열 정보를 저장할 때 사용합니다.
    title = models.CharField(max_length=200)
    # models.TextField - 글자 수에 제한이 없는 긴 텍스트를 위한 속성입니다. 블로그 콘텐츠를 담기 좋겠죠?
    text = models.TextField()
    # models.DateTimeField - 날짜와 시간을 의미합니다.
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
    # 메서드는 자주 무언가를 되돌려주죠. (return) 그 예로 __str__ 메서드를 봅시다. 
    # 이 시나리오대로라면, __str__를 호출하면 Post 모델의 제목 텍스트(string)를 얻게 될 거에요.
    def __str__(self):
        return self.title

    # <a href="{% url 'post_detail' pk=post.pk %}">Comments: {{ post.approved_comments.count }}</a>
    # 에서 post.approved_comments 함수를 사용해
    def approved_comments(self):
        return self.comments.filter(approved_comment=True)

# 댓글
class Comment(models.Model):
    # dels.ForeignKey의 related_name 옵션은 Post 모델에서 댓글에 액서스할 수 있게 합니다.
    # 역참조 대상인 Post에서 comment를 접근할 수 있음
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    # models.BooleanField - 참/거짓(true/false) 필드랍니다.
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text

class AccountManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            # normalize_email()이거는 @domain에서 domain만 소문자로 만듬
            email = self.normalize_email(email),
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )

        # https://docs.djangoproject.com/en/3.2/ref/contrib/auth/
        user.is_admin = True
        user.is_active=True
        user.is_superuser = True
        user.save()

# drf login
# https://medium.com/geekculture/register-login-and-logout-users-in-django-rest-framework-51486390c29
# https://github.com/django/django/blob/910ecd1b8df7678f45c3d507dde6bcb1faafa243/django/contrib/auth/base_user.py#L16 참조하기
# my는 빼도됨 이름에 있을 이유가없음
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True, default=None)
    password = models.CharField(verbose_name='password',max_length=16)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
   
    USERNAME_FIELD = 'email'

    objects = AccountManager()

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return str(self.email)