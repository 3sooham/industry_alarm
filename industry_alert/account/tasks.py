# Create your tasks here
from celery import shared_task
import requests
from esi.serializers import IndustryJobSerializer
from .serializers import EveAccessTokenSerializer
from esi.models import IndustryJob
from .models import User, EveAccessToken
from rest_framework import serializers

import os
from dotenv import load_dotenv
import base64
import datetime

# 주기적으로 task calling 하기
@shared_task()
def temp_task(a, b):
     return a + b


def esi_request(character_id, access_token):

     acc = f'Bearer {access_token}'
     # 처음에 가지고 있던 access token으로 시도 해봄
     # try:
     #      url = f'https://esi.evetech.net/latest/characters/{str(character_id)}/industry/jobs/?datasource=tranquility'
     #      res = requests.get(
     #           url,
     #           headers={"Authorization": acc}
     #      )
     #      # 이거하면 리스트로옴
     #      industry_jobs = res.json()
     #      industry_job_status = industry_jobs[0]['status']
     #
     # except IndexError:
     #      return {"error": "there is no industry job"}
     # except KeyError:
     #      return {"error": "faild to establish connection to eve server"}

     # print("in esi_request : ", character_id, access_token)
     url = f'https://esi.evetech.net/latest/characters/{str(character_id)}/industry/jobs/?datasource=tranquility'
     res = requests.get(
          url,
          headers={"Authorization": acc}
     )
     # 이거 성공하면 리스트로옴
     industry_jobs = res.json()

     # print("in esi_request : ", industry_jobs)

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
     except KeyError:
          return {"status": "failed", "errors": "이브서버와 통신을 실패했습니다."}

     eve_user = dict()
     eve_user['email'] = user.email
     eve_user['name'] = user.name
     eve_user['password'] = user.password
     eve_user['character_id'] = user.character_id

     data_dict = res_dict.copy()
     data_dict['user'] = eve_user

     serializer = EveAccessTokenSerializer(instance, data=data_dict)
     try:
          serializer.is_valid(raise_exception=True)
          serializer.save()
     except serializers.ValidationError:
          return {"status": "failed login user via eve account", "errors": serializer.errors}

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
          return {"status": "failed", "errors": serializer.errors}
     return serializer.data

# async task니까 리턴해줄 필요없음
# 리턴하면 celery resutls에 저장됨
@shared_task()
def get_industry_jobs(character_id, access_token, eve_user_email):
     # get access token from database

     # esi request
     industry_jobs = esi_request(character_id, access_token)
     # 실패했을 경우 dict로 옴
     if isinstance(industry_jobs, dict):
          errors = industry_jobs.get('error')
          # 토큰 만료됐으면
          if errors == 'token is expired':
               # refresh token
               user = User.objects.get(character_id=character_id)
               instance = EveAccessToken.objects.get(access_token=access_token)
               access_token = refresh_access_token(user, instance)

               print("in get_industry_jobs : " ,access_token)
               industry_jobs = esi_request(character_id, access_token['access_token'])
               errors = industry_jobs.get('error')
               # 여기서 실패해도 에러 리턴
               if isinstance(industry_jobs, dict):
                    return industry_jobs

              # 성공하면 저장
               return save_jobs(eve_user_email, industry_jobs)

          # 토큰에러가 아닌 다른 에러일 경우 에러 리턴
          return industry_jobs

     # 에러 없을 경우 저장
     return save_jobs(eve_user_email, industry_jobs)


     # # esi request가  성공했으면
     # # 이 부분을 2번쓰니까 함수로 만들어야함
     # user = User.objects.get(email=eve_user_email)
     # # 잡 생성/업데이트
     # # many=true면 dict가 아닌 list를 넘겨야함
     # serializer = IndustryJobSerializer(data=industry_jobs, many=True, context={'user': user})
     # try:
     #      serializer.is_valid(raise_exception=True)
     #      serializer.save()
     # except serializers.ValidationError:
     #      return {"status": "failed", "errors": serializer.errors}
     # return serializer.data


@shared_task
def periodic_task():
     # task_result = []
     # 이브로 회원 가입한 유저들 가져옴
     instance = User.objects.filter(character_id__gt=0)
     for user in instance:
          access_token = EveAccessToken.objects.get(user=user)
          # esi_result = get_industry_jobs.delay(user.character_id, access_token.access_token, user.email)
          get_industry_jobs.delay(user.character_id, access_token.access_token, user.email)
          # task_result.append(esi_result)

     # return task_result