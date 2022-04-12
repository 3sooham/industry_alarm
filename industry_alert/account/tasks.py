# Create your tasks here
from decimal import DefaultContext
from celery import shared_task
import requests
from esi.serializers import IndustryJobSerializer, FacilitySerializer
from esi.models import IndustryJob, Facility
from eve.models import InvTypes, RamActivity
from .models import User, EveAccessToken
from rest_framework import serializers

import os
from dotenv import load_dotenv
import base64
import datetime

from collections import defaultdict

def esi_request(esi, id, access_token):
     api = {'structures' : f'/universe/structures/{id}/',
            'stations' : f'/universe/stations/{id}/',
            'industry_jobs' : f'/characters/{id}/industry/jobs/',
            'corporations' : f'/corporations/{id}/',
            'systems' : f'/universe/systems/{id}/'
     }
     
     acc = f'Bearer {access_token}'
     url = f'https://esi.evetech.net/latest{api[esi]}?datasource=tranquility'

     try:
          res = requests.get(
               url,
               headers={"Authorization": acc}
          )
          esi_response = res.json()
          res.raise_for_status()
     # 에러 있으면 에러 기록하고 종료함
     # if res.status_code == 304:
     #    raise raise Exception(f'esi={esi} id={id} url={api[esi]} access_token={access_token} esi_response={esi_response})
     except requests.exceptions.HTTPError as e:
          if esi_response['error'] == 'token is expired':
               return 'token is expired'
          raise Exception(f'ESI_REQUEST() esi={esi} id={id} url={api[esi]} access_token={access_token} esi_response={esi_response}, http_error={e}')

     # 에러 없으면 response return 해줌
     return esi_response

def is_station(id, access_token):
     facility = esi_request('stations', id, access_token)
     corporation = esi_request('corporations', facility['owner'], access_token)
     solar_system = esi_request('systems', facility['system_id'], access_token)

     facility['facility_id'] = id
     facility['owner_name'] = corporation['name']
     facility['owner_ticker'] = corporation['ticker']
     facility['type_name'] = InvTypes.objects.get(typeId=facility['type_id']).typeName
     facility['solar_system'] = solar_system['name']
 
     return facility

def is_structure(id, access_token):
     facility = esi_request('structures', id, access_token)
     corporation = esi_request('corporations', facility['owner_id'], access_token)
     solar_system = esi_request('systems', facility['solar_system_id'], access_token)

     facility['facility_id'] = id
     facility['owner_name'] = corporation['name']
     facility['owner_ticker'] = corporation['ticker']
     facility['type_name'] = InvTypes.objects.get(typeId=facility['type_id']).typeName
     facility['solar_system'] = solar_system['name']
     return facility

def insert_facility(industry_jobs, access_token):
     facilities = dict()
     name = EveAccessToken.objects.get(access_token=access_token).user.name

     for job in industry_jobs:
          id = job['facility_id']
          # facility_id가 디비에 있으면 db에 있는거 불러와서 job['facility_id']에 넣어줘야함
          # 이거 근데 스트럭쳐 주인 바뀌면 주인 갱신도 해줘야하는데 어떻게??
          # 따로 주기적으로 facility만 갱신하는 task 있어야할 것 같음
          try:
               # facilities에 unique 한 job_id를 키로 facility_instance를 넣어줌
               # 이거 facility 찾으면 dict에 추가하던지 해서 계속 db hit 안하도록 해야함 -> 그전에 get() 하면 db hit 하는거임??
               facilities[job['job_id']] = Facility.objects.get(facility_id=id)
          # 저장된 facility가 없으면
          except Facility.DoesNotExist:
               # 스테이션
               if id < 100000000:
                    facility = is_station(id, access_token)
               # 스트럭쳐
               else:
                    facility = is_structure(id, access_token)
               
               # facility instance 생성해줌
               serializer = FacilitySerializer(data=facility)
               try:
                    serializer.is_valid(raise_exception=True)
                    facility_instance = serializer.save()
               except serializers.ValidationError:
                    raise Exception(serializer.errors)

               facilities[job['job_id']] = facility_instance

          # blueprint_id로 db에서 blueprint이름 가져와서 job['blueprint']에다가 넣어줌
          job['blueprint'] = InvTypes.objects.get(typeId=job['blueprint_type_id']).typeName
          # django.db.utils.IntegrityError: (1062, "Duplicate entry '1' for key 'blog_post.PRIMARY'")
          job['installer_id'] = name

     return facilities
     
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
          # HTTPError
          # 이거 지금 다시 바꿔야함 raise_for_status의 Exception 처리에서 토큰 지우기 처리해야함
          # res.raise_for_status
          res_dict = res.json()
          res_dict['access_token']
          # jwt 받은거 validate 해야함
          # 그리고 이거 view에서 callback() 뷰랑 이거랑 합쳐서 함수하나 만들어가지고 그거로 한번에 하도록 해야할 것 같음.
          # https://github.com/esi/esi-docs/pull/69/files
          # 이거 이렇게 하지말고 JWT decode 하면 시간 나오니까 그거로 넣어주면됨. 
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

def save_jobs(eve_user_email, industry_jobs, context):
     user_instance = User.objects.get(email=eve_user_email)
     context['user'] = user_instance

     # 잡 생성/업데이트
     # many=true면 dict가 아닌 list를 넘겨야함
     serializer = IndustryJobSerializer(data=industry_jobs, many=True, context=context)
     try:
          serializer.is_valid(raise_exception=True)
          serializer.save()
     except serializers.ValidationError:
          raise Exception({"status": "failed", "errors": serializer.errors, "industry_jobs" : industry_jobs})
     return serializer.data

# async task니까 리턴해줄 필요없음
# 리턴하면 celery resutls에 저장됨
@shared_task()
def get_industry_jobs(character_id, access_token, eve_user_email):

     industry_jobs = esi_request('industry_jobs', character_id, access_token)

     # 토큰 만료됐으면
     if industry_jobs == 'token is expired':
          # refresh token
          user = User.objects.get(character_id=character_id)
          eve_access_token_instance = EveAccessToken.objects.get(access_token=access_token)
          # refresh token으로 access 토큰 갱신해줌
          access_token = refresh_access_token(user, eve_access_token_instance)

          # 새로 발급 받은 토큰으로 다시 esi request함
          industry_jobs = esi_request('industry_jobs', character_id, access_token)

          # context에 facility instance들 넣어줌
          context = insert_facility(industry_jobs, access_token)

          return save_jobs(eve_user_email, industry_jobs, context)

     # context에 facility instance들 넣어줌
     context = insert_facility(industry_jobs, access_token)

     return save_jobs(eve_user_email, industry_jobs, context)

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