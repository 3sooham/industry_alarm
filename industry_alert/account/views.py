from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import EveAccessToken, User
from .serializers import LoginSerializer, UserSerializer, EveUserSerializer, EveAccessTokenSerializer, InvalidPassword

# eve login
import requests
import base64
from dotenv import load_dotenv
import os
from .utils import url_creator, email_creator, create_random_string

# eve token
import datetime

# class EsiIndustryJobsViewSet(viewsets.ModelViewSet):
    # queryset = Industryjobs.objects.all()
    # serializer_class = IndustryJobsSerializer


# 이브 로그인 관련
class EveLoginViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = EveUserSerializer


    def save_eve_access_token(self, res_dict):
        # 이브 토큰 db에 저장하는데 user랑 onetoone이기 때문에 user를 먼저 생성하고 이거를 생성해야함
        # res_dict의 expires_in 이거를python datetime format으로 바꿔서 넣어줘야함
        serializer = EveTokenSerializer(data=res_dict)
        try:
            print("in func eve_access_token", res_dict)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print("in func eve__access_token", serializer.data)
        except serializers.ValidationError:
            return Response({"status": "failed", "errors": serializer.errors})

    @action(methods=['get'], detail=False)
    def callback(self, request):
        # get()
        # Returns the value for key in the dictionary; if not found returns a default value.
        # Optional. 
        # Value that is returned when the key is not found. Defaults to None, so that this method never raises a KeyError.
        
        # 저쪽에서 이쪽으로 request 보낸거는 정상으로 간주하고 해야함
        auth_code = request.GET.get('code')
        state = request.GET.get('state')

        # Now that your application has the authorization code, 
        # it needs to send a POST request to
        # https://login.eveonline.com/v2/oauth/token
        # where your application’s client ID will be the user
        #  your secret key will be the password
        load_dotenv()
        client_id = os.getenv('ID')
        secret_key = os.getenv('KEY')

        # You will need to send the following HTTP headers (replace anything between <>, including <>)
        # Authorization: Basic <URL safe Base64 encoded credentials>
        # Content-Type: application/x-www-form-urlencoded
        # Host: login.eveonline.com
        user_pass = f'{client_id}:{secret_key}'
        basic_auth = base64.urlsafe_b64encode(user_pass.encode()).decode()
        auth_header = f'Basic {basic_auth}'

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "login.eveonline.com",
        }
        body = {
            'grant_type': 'authorization_code',
            'code': auth_code
        }

        # Finally, send a POST request to https://login.eveonline.com/v2/oauth/token with your form encoded values and the headers from the last step.
        try:
            res = requests.post(
                'https://login.eveonline.com/v2/oauth/token',
                headers=headers,
                data=body
            )
            # If the previous step was done correctly, the EVE SSO will respond with a JSON payload containing an access token (which is a Json Web Token) 
            # and a refresh token that looks like this (Anything wrapped by <> will look different for you):
            res_dict = res.json()
            # access_token = res_dict.get('access_token')
            # get()은 default를 return 하니때문에 keyerror생성안하니 get()이거 쓰면 안됨
            access_token = res_dict['access_token']
            res_dict['expires_in'] = datetime.datetime.now() + datetime.timedelta(minutes=19, seconds=59)
            # 이거 어차피 여기서 access_token이 안온거면 연결이  실패한거임
            # 그러니까 예외는 여기서 keyError하나만 잡고 나머지 다른 에러는
            # django에서 500에러 주니 이거 logging 해서 잡아내면됨
            # 클라이언트는 잡다한 예외 상황 알 필요없고 여기 기준으로는 이브와의 서버 통신을 실패한거만 알면 되기 떄문에
            # 그냥 access_token 없으면 이브 서버와의 통신이 실패한거니 실패했다고 알려주면됨.
        except KeyError:
            return Response({"status": "failed", "errors": "이브서버와 통신을 실패했습니다."})

        # 여기서 말하는 JSON payload가 위의 res에 저장됨

        # access_token으로 eve character name 가져옴
        acc = 'Bearer ' + access_token
        try:
            character_res = requests.get(
                "https://login.eveonline.com/oauth/verify",
                headers={"Authorization": acc}
            )
            character_dict = character_res.json()
            character_id = character_dict['CharacterID']
        except KeyError:
            return Response({"status": "failed", "errors": "이브서버와 통신을 실패했습니다."})

        # create django user and return its token
        # eve_user = {} 이렇게 하는거보다 {}이 set, dictionary 둘 다여서 dict()해주는게 좋음
        eve_user = dict()
        eve_user_email = email_creator(character_dict['CharacterName'])
        eve_user['email'] = eve_user_email
        eve_user['name'] = character_dict['CharacterName']
        eve_user['password'] = create_random_string()

        temp_dict = res_dict.copy()
        temp_dict['user'] = eve_user

        serializer = EveAccessTokenSerializer(data=temp_dict)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except serializers.ValidationError:
            return Response({"status": "failed login user via eve account", "errors": serializer.errors})


# drf login
# https://stackoverflow.com/questions/26906630/django-rest-framework-authentication-credentials-were-not-provided 이거 지금 해결안되고있음
class AccountViewSet(viewsets.GenericViewSet):
    # permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # @action은
    # This decorator can be used to add any custom endpoints that don't fit into the standard create/update/delete style.
    # @action decorator will respond to GET requests by default.
    # We can use the methods argument if we wanted an action that responded to POST requests.
    # /.../foo/bar나
    # /.../foo/{pk}/bar
    # 이런 api를 추가하고싶을때쓰는거임
    # detail=False면 위 detail=True면 아래

    # @action(detail=True, methods=['get'])
    # def asd(self, request, pk):
    # 이거면 http://localhost:8000/test/login/[pk]/asd 여기로 등록됨
    # detail=False여야지만 http://localhost:8000/test/login/asd/로 감
    # http GET http://127.0.0.1:8000/api/v1/user/asd
    @action(methods=['get'], detail=False, permission_classes=[AllowAny])
    def asd(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    # /api/v1/user 로 GET요청 받을 user list api (UserSerializer 사용)
    # http GET http://127.0.0.1:8000/api/v1/user "Authorization: Token 01ecad58c74bb6a6c52ab3f8cb6946cb7312e0d6"
    def list(self, request):
        # self.get_queryset() 이거로 queryset = User.objects.all() 이거 가져오는거임
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # /api/v1/user/pk 로 GET요청 받을 user retrieve api (UserSerializer사용)
    # http GET http://127.0.0.1:8000/api/v1/user/48 "Authorization: Token 01ecad58c74bb6a6c52ab3f8cb6946cb7312e0d6"
    def retrieve(self, request, pk):
        # queryset과 pk값을 인자로 받아서,
        # queryset.filter(pk=pk)로 queryset을 뽑고,
        # instance = queryset.get()으로 객체만 뽑아서 리턴해 주는 메소드임
        # => 결국, 위 코드는 Customer.objects.get(pk=pk) 리턴함
        # https://velog.io/@jcinsh/RetrieveUpdateDestroyView-%EC%9D%B4%ED%95%B4 참조
        # queryset = User.objects.all() 이거를 기반으로 하는거임
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # /api/v1/user/pk 로 PATCH 요청 받을 user update ap
    # http PUT http://127.0.0.1:8000/api/v1/user/50 "Authorization: Token 01ecad58c74bb6a6c52ab3f8cb6946cb7312e0d6"
    # 이거 비밀번호를 바꾸려면 userserilaier에서 비밀번호가 readonly여서 안보이니 비밀번호를 바꾸려면 serializer를 새로 만들어야함
    def update(self, request, pk):
        instance = self.get_object()
        # data앞에 뭐가 있으니 업데이트함
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except serializers.ValidationError:
            return Response({"status": "failed", "errors": serializer.errors})

    # /api/v1/user/pk 로 DELETE 요청 받을 user delete api (Serializer 사용 x)
    # http DELETE http://127.0.0.1:8000/api/v1/user/2000 "Authorization: Token 01ecad58c74bb6a6c52ab3f8cb6946cb7312e0d6"
    def delete(self, request, pk):
        print("in delete")
        instance = self.get_object()
        instance.delete()
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)

    # /api/v1/user 로 POST요청을 받을 registration api (UserSerializer 사용)
    # http POST http://127.0.0.1:8000/api/v1/user/register email="id@gmail.com" password="pw"
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request, eve_user=None):
        print("in register")
        print(eve_user)
        if eve_user:
            serializer = self.get_serializer(data=eve_user)
            try:
                serializer.is_valid(raise_exception=True)
                # 이거 save()했을때 불려오는 method는
                # serializer = UserSerializer(data=request.data)에서 data앞에 뭐가 없으면
                # UserSerializer.create()를 불러오는거임
                serializer.save()
                # 이거 pw는 write_only라서 안보임
                print("in register2")
                print(serializer.data)
                return Response(serializer.data)
            except serializers.ValidationError:
                return Response({"status": "failed", "errors": serializer.errors})
        else: 
            serializer = self.get_serializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
                # 이거 save()했을때 불려오는 method는
                # serializer = UserSerializer(data=request.data)에서 data앞에 뭐가 없으면
                # UserSerializer.create()를 불러오는거임
                serializer.save()
                # 이거 pw는 write_only라서 안보임
                print(serializer.data)
                return Response(serializer.data)
            except serializers.ValidationError:
                return Response({"status": "failed", "errors": serializer.errors})

    # /api/v1/user/login 으로 POST요청을 받을 login api (LoginSerializer 사용)
    # http POST http://127.0.0.1:8000/api/v1/user/login email="id@gmail.com" password="pw"
    # 로그아웃 안하고 서버가 그냥 닫아지면 토큰 값이 유지되는거 같음 어떻게 해결해야함?
    # 이거 get_or_create로 하기때문에 같은거임 안그러면 서버껐다켰는데 애들다 토큰 날아가서 다 에러나거나 로그인페이지로 날아감
    # 해결하기 위해서는 토큰에 만료기한을 두고 토큰유출대도 credential이 없으면 만료시점이후에는 무효처리되도록 다시로그인시켜보는거지
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except InvalidPassword:
            return Response({'success': False, 'error': '패스워드가 일치하지 않습니다'}, status=status.HTTP_400_BAD_REQUEST)
        # 이거는 user = User.objects.get(email=email)에서 없으면 자동으로 raise됨
        except User.DoesNotExist:
            return Response({'success': False, 'error': '유저가 존재하지 않습니다'}, status=status.HTTP_400_BAD_REQUEST)

    # /api/v1/user/logout 으로 DELETE 요청을 받을 logout api(Serializer 사용 x)
    # http POST http://127.0.0.1:8000/api/v1/user/logout "Authorization: Token f44c39fec18227d5aa555dcbd20aa7d56d0f55ef"
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        request.user.auth_token.delete()

        return Response({'success': "로그아웃 성공"}, status=status.HTTP_200_OK)

    # 특정 유저가 publish 한 post 보기
