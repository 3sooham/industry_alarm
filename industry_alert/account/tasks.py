# Create your tasks here
from celery import shared_task
import requests
from esi.serializers import IndustryJobSerializer
from esi.models import IndustryJob
from .models import User, EveAccessToken
from rest_framework import serializers

import os
from dotenv import load_dotenv
import base64
import datetime

def esi_request(esi, id, access_token):
     api = [f'/universe/structures/{id}/',
            f'/universe/stations/{id}/',
            f'/characters/{id}/industry/jobs/',       
     ]
     
     acc = f'Bearer {access_token}'
     url = f'https://esi.evetech.net/latest{api[esi]}?datasource=tranquility'

     try:
          res = requests.get(
               url,
               headers={"Authorization": acc}
          )
          # 이거 성공하면 리스트로옴
          esi_response = res.json()
     except requests.exceptions.HTTPError as e:
          raise e

     return esi_response

def esi_request_industry_jobs(character_id, access_token):

     acc = f'Bearer {access_token}'
     url = f'https://esi.evetech.net/latest/characters/{str(character_id)}/industry/jobs/?datasource=tranquility'

     try:
          res = requests.get(
               url,
               headers={"Authorization": acc}
          )
          # 이거 성공하면 리스트로옴
          industry_jobs = res.json()
     except requests.exceptions.HTTPError as e:
          raise e

     return industry_jobs

# 갱신하는 토큰으로 새 토큰 받아옴
def refresh_access_token(user, instance):
     load_dotenv()
     client_id = os.getenv('ID')
     secret_key = os.getenv('KEY')

     user_pass = f'{client_id}:{secret_key}'
     basic_auth = base64.urlsafe_b64encode(user_pass.encode()).decode()
     auth_header = f'Basic {basic_auth}'

     headers = {
          "Authorization": auth_header,
          "Content-Type": "application/x-www-form-urlencoded",
          "Host": "login.eveonline.com"
     }
     body = {
          'grant_type': 'refresh_token',
          'refresh_token': instance.refresh_token
     }
     try:
          res = requests.post(
               'https://login.eveonline.com/v2/oauth/token',
               headers=headers,
               data=body,
          )
          res_dict = res.json()
          access_token = res_dict['access_token']
          res_dict['expires_in'] = datetime.datetime.now() + datetime.timedelta(minutes=19, seconds=59)
     except requests.exceptions.HTTPError as e:
          raise e
     except KeyError:
          # 이거 그냥 유저를 삭제하는 식으로 해도되는데 유저가 게시판 기능을 추가할거면
          # 삭제하면 안될것같아서 유저는 남겨둘거임

          # esi 권한 회수등으로 invalid 한 refresh token이면 access_token 삭제해줌
          instance = EveAccessToken.objects.get(user=user)
          instance.delete()

          # 이러면 해당 유저로 저장된 인더잡도 다 지우고
          instance = IndustryJob.objects.filter(user__exact=user)
          instance.delete()
          # 해당 유저의 장고 토큰도 없애줌
          # 이거는 잘모르겠음 물어봐야할거같음

          raise Exception(res_dict)

     eve_user = dict()
     eve_user['email'] = user.email
     eve_user['name'] = user.name
     eve_user['password'] = user.password
     eve_user['character_id'] = user.character_id

     data_dict = res_dict.copy()
     data_dict['user'] = eve_user

     # circular import 방지
     from .serializers import EveAccessTokenSerializer
     serializer = EveAccessTokenSerializer(instance, data=data_dict)
     try:
          serializer.is_valid(raise_exception=True)
          serializer.save()
     except serializers.ValidationError:
          raise Exception({"status": "failed login user via eve account", "errors": serializer.errors})

     return serializer.data

def save_jobs(eve_user_email, industry_jobs):
     user = User.objects.get(email=eve_user_email)

     # 잡 생성/업데이트
     # many=true면 dict가 아닌 list를 넘겨야함
     serializer = IndustryJobSerializer(data=industry_jobs, many=True, context={'user': user})
     try:
          serializer.is_valid(raise_exception=True)
          serializer.save()
     except serializers.ValidationError:
          raise Exception({"status": "failed", "errors": serializer.errors})
     return serializer.data

# async task니까 리턴해줄 필요없음
# 리턴하면 celery resutls에 저장됨
@shared_task()
def get_industry_jobs(character_id, access_token, eve_user_email):
     # esi request
     industry_jobs = esi_request_industry_jobs(character_id, access_token)
     # 실패했을 경우 dict로 옴
     if isinstance(industry_jobs, dict):
          errors = industry_jobs.get('error')
          # 토큰 만료됐으면
          if errors == 'token is expired':
               # refresh token
               user = User.objects.get(character_id=character_id)
               instance = EveAccessToken.objects.get(access_token=access_token)
               # refresh token으로 access 토큰 갱신해줌
               access_token = refresh_access_token(user, instance)

               # 새로 발급 받은 토큰으로 다시 esi request함
               industry_jobs = esi_request_industry_jobs(character_id, access_token['access_token'])

               # 실패하면 dict로옴
               if isinstance(industry_jobs, dict):
                    raise Exception(industry_jobs)

               # 가져온 잡들에서 facility_id만 분리해서 이거 다시 esi_request해서 넣어줘야함
               for job in industry_jobs:
                    id = job['facility_id']
                    # 스테이션
                    if id < 100000000:
                         # 이거 그냥 하는것도 리스트로 오는지 확인해야함
                         result = esi_request(1, id, access_token)
                    # 스트럭쳐
                    else:
                         result = esi_request(0, id, access_token)
                    
                    try:
                         error = result['error']
                    except:
                         print('************************')
                         print(f'나는 스트럭쳐 에러{result}, {User.objects.get(character_id=character_id)}')
                         print('************************')
                    print('zzzzzzzzzzzzzzzzzzzzz')
                    # from eve.models import Eve
                    print(result)
                    print('zzzzzzzzzzzzzzzzzzzzzzzz')
                    # job['facility_id'] = result

              # 성공하면 저장
               return save_jobs(eve_user_email, industry_jobs)

          # 토큰 만료가 아닌 다른 에러일 경우
          raise Exception(industry_jobs)

     # 에러 없을 경우 esi로 가져온 인더잡들 저장
     return save_jobs(eve_user_email, industry_jobs)

@shared_task
def periodic_task():
     # task_result = []
     # 이브로 회원 가입한 유저들 가져옴
     instance = User.objects.filter(character_id__gt=0)
     for user in instance:
          try:
               access_token = EveAccessToken.objects.get(user=user)
               get_industry_jobs.delay(user.character_id, access_token.access_token, user.email)
          # access token 없는 계정이면 인더잡 가져오는거 건너뜀
          # access token은 revoke 등으로 인해서 없을수가 있음
          except EveAccessToken.DoesNotExist:
               pass

     return 'periodic_task()'