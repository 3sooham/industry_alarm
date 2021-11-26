# Create your tasks here
from celery import shared_task
import requests
from esi.serializers import IndustryJobSerializer
from esi.models import IndustryJob
from .models import User, EveAccessToken
from rest_framework import serializers


# 주기적으로 task calling 하기
@shared_task()
def temp_task(a, b):
     return a + b

@shared_task()
def periodic_task1():
     task_result = []
     # 이브로 회원 가입한 유저들 가져옴
     instance = User.objects.filter(character_id__gt=0)
     for user in instance:
          access_token = EveAccessToken.objects.filter(user)
          esi_result = esi_reqeust(instance.character_id, access_token.access_token)

          error = esi_result.get('error')
          # 토큰이 만료됐으면
          if error == 'token is expired':
               # refresh access token with a refresh token
               access_token = refresh_access_token(user, access_token)

               # 다시 esi_request
          # 인더잡을 잘 가져왔으면
          elif error == None:
               # 잡 가져온거 저장해줘야함
               pass
          else:
               task_result.append(error)

     return task_result

# db에 job 저장
def save_industry_jobs(industry_jobs, user):
     # 잡 생성/업데이트
     serializer = IndustryJobSerializer(data=industry_jobs, many=True, context={'user': user})
     try:
          serializer.is_valid(raise_exception=True)
          serializer.save()
     except serializers.ValidationError:
          return {"status": "failed", "errors": serializer.errors}
     return serializer.data

# 갱신하는 토큰으로 새 토큰 받아옴
def refresh_access_token(user, access_token):

     # get new token with a refresh token

     serializer = EveAccessTokenSerializer(access_token, data=temp_dict)
     try:
          serializer.is_valid(raise_exception=True)
          instance = serializer.save()
     except:
          pass

     return instance

def esi_reqeust(character_id, access_token):

     acc = f'Bearer {access_token}'
     # 처음에 가지고 있던 access token으로 시도 해봄
     try:
          url = f'https://esi.evetech.net/latest/characters/{str(character_id)}/industry/jobs/?datasource=tranquility'
          res = requests.get(
               url,
               headers={"Authorization": acc}
          )
          # 이거하면 리스트로옴
          industry_jobs = res.json()
          industry_job_status = industry_jobs[0]['status']

          return industry_jobs
     except IndexError:
          return {"error": "there is no industry job"}
     except KeyError:
          return {"error": "faild to establish connection to eve server"}


# async task니까 리턴해줄 필요없음
# 리턴하면 celery resutls에 저장됨
@shared_task()
def get_industry_jobs(character_id, access_token, eve_user_email):
     # get access token from database

     # esi request
     industry_jobs = esi_reqeust(character_id, access_token)

     # esi request 실패했으면 에러 리턴
     if esi_result.get('error'):
         return industry_jobs

     # esi request가  성공했으면
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
