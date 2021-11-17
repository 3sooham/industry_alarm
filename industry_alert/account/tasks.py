# Create your tasks here
from celery import shared_task
import requests
from esi.serializers import IndustryJobSerializer
from esi.models import IndustryJob
from rest_framework import serializers

# async task니까 리턴해줄 필요없음
@shared_task()
def get_industry_jobs(character_id, user_instance):
     # esi request
     try:
          url = f'https://esi.evetech.net/latest/characters/{str(character_id)}/industry/jobs/?datasource=tranquility'
          res = requests.get(
               url2,
               headers={"Authorization": acc}
          )
          industry_jobs = res.json()
          industry_job_status = industry_jobs['status']
     except:
          logger.info('failed to establish connection to esi server', exc_info=1)

     objs_need_update = []
     data_need_update = []
     data_need_create = []

     print("in task")
     # # 이 유저로 저장된 job이 없을 경우 전부 생성만 하면됨
     # if not IndustryJob.objects.filter(user=user_instance).exists():
     #      pass
     #
     # # 이거 삭제도 해야함
     # # 이 유저로 저장된 job이 있을 경우에
     # for job in industry_jobs:
     #      # job_id로 db에 job이 있는지 찾아봄
     #      instance = IndustryJob.objects.filter(job_id=job['job_id'])
     #      # job이 db에 존재하고 status가 바뀌었으면 업데이트 해줌
     #      # 근데 이거 업데이트 하는게 status밖에 없는거 같은데 status가 정확이 뭘하는지를 모르겠음
     #      if instance.exists() and instance.status != industry_jobs['status']:
     #           objs_need_update.append(instance)
     #           data_need_update.append(job)
     #      # 없으면 생성할 거에 넣어줌
     #      elif not instance.exists():
     #           data_need_create.append(job)
     #
     # industry_jobs['user'] = user_instance
     # instance = IndustryJob.objects.filter(user=user_instance)
     # # esi로 불러온 인더잡 업데이트/저장
     # serializer = IndustryJobSerializer(instance, data=request.data, partial=True)
     # try:
     #      serializer.is_valid(raise_exception=True)
     #      serializer.save()
     # except:
     #      logger.info('failed to update/save industry jobs into db', exc_info=1)