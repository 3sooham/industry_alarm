from requests.api import get
from rest_framework import serializers
from .models import User, EveAccessToken
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .utils import create_random_string
# get_user_model() : 클래스이다.
# >>> get_user_model()
# <class 'accounts.models.User'>
# settings.AUTH_USER_MODEL : 문자열이다.
# >>> settings.AUTH_USER_MODEL
# >>> settings.AUTH_USER_MODEL
# 'accounts.User'

# exceptions
class InvalidPassword(Exception):
    pass


class EveTokenSerializer(serializers.ModelSeraizlier):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class meta:
        model = EveAccessToken
        fields = ['id', 'user_id', 'access_token', 'expires_in', 'token_type', 'refresh_token']


class CommentSerializer(serializers.ModelSerializer):
    # 이거 read_only는 이걸 serialize 했을때 
    # [
    #   {
    #     "id": number,
    #     "post": number
    #   }
    # ]
    # 위와 같은 결과물을 만들고 싶다는 거임
    # post = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    # 이 두 필드를 requests로 받는게 아니라 강제로 지정할 거기 때문에 required=False로 함함
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    # 이거 post로 하면 Post 인스턴스라서 안돼고
    # 이렇게 _id 붙여서 id int로 바꿔야함
    # 이 related field들은 다 이럼
    # django 기본 queryset이 걍 이런거임
    # 이 related field들이 fk constraint말고도 실제로 칼럼이름이 post_id로 저장되어 있음
    # post_id같이 (related_field이름)_id 이런식으로 실제 db에 기록대고
    # 이게 본체인거고 저런 post 같은게 장고가 알아서 해주는 부분인데
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), required=False)

    class Meta:
        model = Comment
        fields = ['id', 'post_id', 'author', 'text', 'created_date', 'approved_comment']

    # is_valid가 3가지 검사를 함
    # model에 정의된거랑 타입이 맞는지 필드별로 검사 한 번 다 하고
    # serializer에 validate_필드이름 이렇게 정의한 함스들 코드에서 파싱해서 저 함수들 한번씩 다 돌려주고
    # 각 필드에 대한 추가적인 validation임
    # 그 다음에 validate() 한번 실행하고 결과값을 validated_data로 
    # create나 update 메서드에 넘겨줌
    # def validate(self, attr):
    #        return attr
    # 이거는 원래 비어있음
    def validate(self, attr):
        # 이거는 request 전부가 serializer로 감
        # self.context['view'].action 이거로 더 자세한 정보 볼 수 있음
        # 어떤 함수 불러온지 알 수 있기 때문임
        author = self.context['request'].user
        if author.is_anonymous:
            raise ValidationError('anonymous user cannot create comment')
        attr['author'] = self.context['request'].user.id
        attr['post_id'] = self.context['post_id']
        return attr

    # Field-level validation
    # 이게 is_valid안에서 완벽히 일치하는거는 아닌데 대충 이런게 돌아감
    # def is_valid(self):
    #     ...
    #     for field in self.Meta.fields:
    #         validate_func = getattr(self, f'validate_{field}')
    #         validate_func(self.initial_data.get(field))
    # 여기서 value는 text임
    def validate_text(self, value):
        if '시벌' in value:
            raise ValidationError('욕하지마라')
        return value


class EveUserSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)
    status = serializers.IntegerField(read_only=True)
    name = serializers.CharField(write_only=True)

    def create(self, validated_data):
        # 유저가 존재할 경우에
        if User.objects.all().filter(email=validated_data['email']).exists():
            email = validated_data['email']
            user = User.objects.get(email=email)
            print(user.name)
            # 위에서 get안되면 exception 뱉어서 여기 안탐
            token, _ = Token.objects.get_or_create(user=user)

            return {'token': token.key, 'status': 200}

        # 유저가 존재하지 않으면 회원가입
        validated_data['password'] = create_random_string()
        user = User.objects.create_user(**validated_data)

        token, _ = Token.objects.get_or_create(user=user)
        user.token = token
        return {"token": token.key, 'status': 201}

# drf
# 1. Serializer를 상속받은 LoginSerializer, 그리고 ModelSerializer를 상속받은 UserSerializer 두 개 작성
# 2. 각 serializer는 아래와 같은 field를 가지고 이름에 맞는 동작을 해야함
# https://eunjin3786.tistory.com/253
# LoginSerializer
#     쓰기전용 : username, password
#     읽기전용 : token
#     동작 : username과 password로 user인증을 하고, user의 token이 있으면 그것을, 없으면 새로 발행해서 돌려줌
class LoginSerializer(serializers.Serializer):
    # write_only는 값을 받아서 create/update같은거만 하는거임
    email = serializers.CharField(write_only=True)
    # required=False
    password = serializers.CharField(write_only=True)
    # 입력받는게 아니라 return으로 돌려주는 값이니까 read_only임
    token = serializers.CharField(read_only=True)

    # 로그인 확인
    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']

        user = User.objects.get(email=email)

        # 비밀번호 일치하면
        if user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            # 이거 그냥 return token 하면 안돼는 이유는
            # 밑의 유저시리얼라이저에서는 user.token에 token.key를 넣어줬는데
            # 이거 리턴되는 object에서 getattr로 리턴 field들이 다 있으면 알아서 만들어주는건데
            # 밑에서는 리턴이 user객체였고 이 객체에는 class Meta에 있는 3개의 field가 다 있어서 문제없이 된거고
            # 지금은 token을 리턴하게 되면 token.token은 없고 token.key에 원하는값이있지
            # 그래서 지금 에러인 {}가 가는거임
            # token을 리턴하면 Token object인데 내가 serializer에 리턴하겠다고 명시한건
            # token이라는 필드고 리턴한걸 serialize했을때 리턴 결과물에 token이라는 attribute가 있어야하는데
            # token.token이 없으니 아무런 결과물이 안나오는거임
            # 이제 {'token': token.key}를 리턴하면 getattr(리턴 결과물, 'token')하면
            # 값이 있으니 결과물이 나오는거임
            # 객체 serialize하면 __str__()로 나오는 결과물이 나옴
            # print(getattr(token, 'key'))
            print(token.key)
            return {'token': token.key}
        # 일치하는 비밀번호가 없으면
        raise InvalidPassword


# UserSerializer
#     둘 다 : 필요한 모든 유저정보들
#     쓰기전용 : password
#     읽기전용 : token
#     동작 : 받은 user정보를 통해 User를 생성하고, 생성된 user의 token을 새로 발행해서 password를 제외한 나머지 정보와 함께 돌려줌
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name', 'token']

    # 이거 근데 user.mode()에서 해주는데 없어야하는거 같음
    # override하는거니까 인자 맞춰줘야함
    def create(self, validated_data):
        print("유저시리얼라이저 - create")
        # 이제 이 validate_data는 validation도 끝났으니 정합한 데이터니 그냥 때려버리면 됨
        # 이거 **은
        # **d means "take all additional named arguments to this function
        # and insert them into this parameter as dictionary entries."
        # 이거 create_user가 인자를 2개 받아야하니 **validated_data
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        # 가져오거나 생성한값이랑
        # 생성됐는지 가져온건지 여부를
        # 튜플로줌
        # 저게 생성으로 가져온 결과물이면 True
        # 있던거 가져온거면 False
        # _는 안쓸값은 _로 저장함
        token, _ = Token.objects.get_or_create(user=user)
        # 이거 가능한 이유는 user는 User의 인스턴스고 파이썬 클래스는 getter setter없이 걍 뭐든 할 수 있어서
        # 이렇게 하면 token이 추가가 가능한거임
        # 추가로 걍 객체를 serialize시키면 아까말한 __str__()값이 들어감
        user.token = token
        # token object의 key가 사용하는 token임
        return {"token": token.key}

    def update(self, instance, validated_data):
        # items()은 key, value 튜플쌍을 튜플로 리턴하는 함수임
        print(instance.password)
        for key, value in validated_data.items():
            # 제일 첫번째 인자에 key가 있으면 True 없으면 False 반환하는게 hasattr이고
            if hasattr(instance, key):
                # 값 저장하는게 setattr
                setattr(instance, key, value)
        instance.save()
        return instance
