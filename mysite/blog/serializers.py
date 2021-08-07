from rest_framework import serializers
from blog.models import Post, Comment

#drf
from django.contrib.auth import get_user_model
# get_user_model() : 클래스이다.
# >>> get_user_model()
# <class 'accounts.models.User'>
# settings.AUTH_USER_MODEL : 문자열이다.
# >>> settings.AUTH_USER_MODEL
# >>> settings.AUTH_USER_MODEL
# 'accounts.User'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        # fieds에 id나 pk로 지정된 필드 꼭 있어야함
        fields = ['id', 'author', 'title', 'text', 'created_date', 'published_date']

class CommentSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'text', 'created_date', 'approve_comment']

# drf
# 1. Serializer를 상속받은 LoginSerializer, 그리고 ModelSerializer를 상속받은 UserSerializer 두 개 작성
# 2. 각 serializer는 아래와 같은 field를 가지고 이름에 맞는 동작을 해야함

# https://eunjin3786.tistory.com/253
# UserSerializer
#     둘 다 : 필요한 모든 유저정보들
#     쓰기전용 : password
#     읽기전용 : token
#     동작 : 받은 user정보를 통해 User를 생성하고, 생성된 user의 token을 새로 발행해서 password를 제외한 나머지 정보와 함께 돌려줌


# LoginSerializer
#     쓰기전용 : username, password
#     읽기전용 : token
#     동작 : username과 password로 user인증을 하고, user의 token이 있으면 그것을, 없으면 새로 발행해서 돌려줌

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password',]

    # 로그인 확인
    def authenticate(self):
        email = self.validated_data['email'],
        password = self.validated_data['password']
        # email에 해당하는 user 불러옴
        # 이거 근데 email에 해당하는 유저가 없으면 처리하는게 있어야할거같음
        user = get_user_model().objects.filter(email=email)
        # 그 해당 user의 비밀번호를 불러옴
        user_password = user.get('password')
        
        if password == user_password:
            return True
        return False

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)   

    class Meta:
        model = get_user_model()
        fields = ['email', 'password']

    def create(self):
        # account는 email, password를 가진 User instance임
        account = get_user_model()(
                    email=self.validated_data['email'],
                    password = self.validated_data['password']
                )
        account.save()
        return account