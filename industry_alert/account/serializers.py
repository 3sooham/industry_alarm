from requests.api import get
from rest_framework import serializers
from .models import User, EveAccessToken, UserLinkInfo
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
# get_user_model() : 클래스이다.
# >>> get_user_model()
# <class 'accounts.models.User'>
# settings.AUTH_USER_MODEL : 문자열이다.
# >>> settings.AUTH_USER_MODEL
# >>> settings.AUTH_USER_MODEL
# 'accounts.User'

# celery task
from .tasks import get_industry_jobs

# exceptions
class InvalidPassword(Exception):
    pass


class UserLinkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLinkInfo
        fields = ['id', 'name']

class EveUserSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    character_id = serializers.IntegerField(write_only=True)

# https://stackoverflow.com/questions/42314882/drf-onetoonefield-create-serializer
class EveAccessTokenSerializer(serializers.Serializer):
    # required=True는 default임
    # 이거 돌려줄 필요없음
    user = EveUserSerializer(write_only=True)
    # 이거 그냥 required=False로 하고 어차피 갱신할때는 instance를 리턴하니까
    # create에서는 access_token 리턴할 필요없음
    access_token = serializers.CharField(required=False)
    expires_in = serializers.DateTimeField(write_only=True)
    token_type = serializers.CharField(write_only=True)
    refresh_token = serializers.CharField(write_only=True)
    # 여기 token 넣어줘야지 create()에서 리턴해줄 수 있음 아니면 serialize를 못함
    token = serializers.CharField(read_only=True)

    class Meta:
        model = EveAccessToken
        fields = ['id', 'user', 'access_token', 'expires_in', 'token_type', 'refresh_token', 'token']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_email = user_data.pop('email')

        # 일단 계정 생성시 링크 만들고
        # A로 처음 로그인하면 A 이름으로 링크 생성함
        # B로 처음 로그인하면 B 이름으로 링크 생성함
        # 이 상태에서 A를 B에 추가하고 싶으면
        # A의 링크를 없애고 B의 이름으로 된 링크에 A를 넣어줌.
        # 이제 한 번도 로그인 한 적이 없는 C를 B에 넣어주고 싶으면
        # C의 계정을 생성하면서 B의 링크에 C를 넣어줌.
        # if self.context['link']:
        #     link_insatce = UserLinkInfo.objects.get(name=self.context['link'])
        #     user_instance, _ = User.objects.get_or_create(email=user_email, defaults=user_data)
            # serializer = EveAccessTokenSerializer(data=temp_dict)
            # try:
            #     serializer.is_valid(raise_exception=True)
            #     serializer.save()

            #     token = serializer.data['token']
            #     # 다 저장했으면 클라이언트로 리다이렉트 해줌.
            #     redirect_url = f'http://localhost:4200/login?token={token}&name={character_dict["CharacterName"]}'
            #     return redirect(redirect_url)

        # else:
        #     user_instance, _ = User.objects.get_or_create(email=user_email, defaults=user_data)
            #  링크 인스턴스 생성 name이 user_instacne.name임
        # context로 {link: name}이 들어오면
        # User.get(name=name).link로 유저를 연결해줘야함
        # 그게 아니라면 유저를 get_or_create해서 해당 유저에 link가 없으면 만들어줌. 
 
        # 계정을 kwargs로 찾고 계정이 없으면 kwargs랑 defaults 둘 다 이용해서 생성해줌
        if self.context is None:
            print("컨텍스트없다!!@!@!@!@!@")
        user_instance, _ = User.objects.get_or_create(email=user_email, defaults=user_data)

        # 내 토큰 발급
        token, _ = Token.objects.get_or_create(user=user_instance)

        # EAT update하거나 생성
        EveAccessToken.objects.update_or_create(user=user_instance, defaults=validated_data)
        # 여기서 return 하는 instance랑 시리얼라이저의 field를 기반으로 serializer.data가 만들어짐
        # 여기서 리턴하는게 field에 있어야만 serializer.data에 들어가는거임
        # 여기서 튜플리턴하는데 없는것들 있어서 안가지는거임
        #   return instance, user_instance, updated, 201, {"token": token.key}

        # celery로 job 받아오기
        get_industry_jobs.delay(user_data['character_id'], validated_data['access_token'], user_email)

        return {"token": token.key}

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user_instance = User.objects.get(email=user_data['email'])
        validated_data['user'] = user_instance

        for key, value in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        instance.save()

        return instance


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
            # print(token.key)
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
        fields = ['email', 'password', 'name', 'character_id', 'token']

    # 이거 근데 user.mode()에서 해주는데 없어야하는거 같음
    # override하는거니까 인자 맞춰줘야함
    def create(self, validated_data):
        # print("유저시리얼라이저 - create")
        # 이제 이 validate_data는 validation도 끝났으니 정합한 데이터니 그냥 때려버리면 됨
        # 이거 **은
        # **d means "take all additional named arguments to this function
        # and insert them into this parameter as dictionary entries."
        # 이거 create_user가 인자를 2개 받아야하니 **validated_data
        # print(validated_data)
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
        # print(instance.password)
        for key, value in validated_data.items():
            # 제일 첫번째 인자에 key가 있으면 True 없으면 False 반환하는게 hasattr이고
            if hasattr(instance, key):
                # 값 저장하는게 setattr
                setattr(instance, key, value)
        instance.save()
        return instance
