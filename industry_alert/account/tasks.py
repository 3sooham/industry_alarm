# Create your tasks here
from celery import shared_task
import requests
from esi.serializers import IndustryJobSerializer
from esi.models import IndustryJob
from rest_framework import serializers


# async task니까 리턴해줄 필요없음
@shared_task()
def get_industry_jobs(character_id):
     # esi request
     try:
          url = f'https://esi.evetech.net/latest/characters/{str(character_id)}/industry/jobs/?datasource=tranquility'
          res = requests.get(
               url,
               headers={"Authorization": acc}
          )
          # 이거하면 리스트로옴
          industry_jobs = res.json()
          industry_job_status = industry_jobs[0]['status']
     # job이 없으면 task 종료
     except IndexError:
          return Response({"status": "there is no industry job"})
     except KeyError:
          return Response({"status": "faild to establish connection to eve server"})

     user = User.objects.get(email=eve_user_email)
     # 잡 생성/업데이트
     # many=true면 dict가 아닌 list를 넘겨야함
     serializer = IndustryJobSerializer(data=industry_jobs, many=True, context={'user': user})
     try:
          serializer.is_valid(raise_exception=True)
          serializer.save()
     except serializers.ValidationError:
          return Response({"status": "failed", "errors": serializer.errors})
     return Response({"validated_data": serializer.data})