from unittest.result import failfast
from unittest.util import _MAX_LENGTH
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Facility(models.Model):
    # id < 100000000 면 NPC 스테이션임
    facility_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    owner_ticker = models.CharField(max_length=255)
    type_name = models.CharField(max_length=255)
    solar_system = models.CharField(max_length=255)

# class IndustryJobManager(models.Manager):
#     @staticmethod
#     def set_status(job, new_status):
#         job.status = new_status
#         return job

#     def bulk_create_or_update(self, validated_data, user):
#         # instance = IndustryJob.objects.filter(user=user) 이건데
#         # 커스텀 매니저를 만들었으니 self로 바꿔줘야함
#         instance = self.filter(user=user)
#         # 유저에 대해서 저장된 잡이 있으면
#         if instance.exists():
#             # 기존에 존재하는 job들을 job_id를 key로 정리
#             # 여기서 iterate하니  db hit 하는거임
#             job_mapping = {job.job_id: job for job in instance}
#             # 새로 받아온 job들을 job_id를 키로 정리
#             data_mapping = {item['job_id']: item for item in validated_data}

#             # 새로 받아온 job이 db에 저장되어 있는지 확인하고 없으면 생성
#             # self.model로 모델 클래스 가져올 수 있음
#             # Another thing to note is that Manager methods can access self.model to get the model class to which they’re attached.
#             need_create = [
#                 self.model(**data) for job_id, data in data_mapping.items() if job_mapping.get(job_id) is None
#             ]
#             # 이거 []들어가면 실행안하고 끝나서 if need_crate: 이렇게 안해도됨
#             self.bulk_create(need_create)

#             # 새로 받아온 job이 db에 저장되어 있고 status가 변경 됐으면 update 해줌
#             # 이거 staticmethod는 불러올때 크래스명
#             need_update = [
#                 self.set_status(job, data_mapping[job_id]['status']) for job_id, job in job_mapping.items()
#                 if job_id in data_mapping.keys() and job.status != data_mapping[job_id]['status']
#             ]
#             self.bulk_update(need_update, ['status'])

#             # 이미 있는 잡이 새로 불러온 job에 없으면 완료되서 사라진거니 삭제해줌
#             # 이거 python gc가 reference기반이어서 아래에서 더이상 안쓰면 알아서 지워줌
#             # 아래 리스트 만들면서 job.delete() 실행하고 다음줄 내려가면서 메모리에서 날아감
#             [job.delete() for job_id, job in job_mapping.items() if job_id not in data_mapping]

#             # bulk_create, bulk_update의 리턴값을 넘겨주지말고 그냥 이렇게 해도됨
#             # 실제로 생성된 것도 아니니까 생성전 데이터만 넣어주기
#             ret = [*need_create, *need_update]
#             if ret:
#                 return ret
#             return validated_data

#         # 유저에 대해서 잡이 없으면 create
#         industry_jobs = [self.model(**item) for item in validated_data]
#         return self.bulk_create(industry_jobs)

# # 클래스명 단수로
# # 이름 붙이는 거는 불려오는곳에서 이름이 얼마나 자연스러운지가 중요함
# class IndustryJob(models.Model):
#     class Status(models.TextChoices):
#         ACTIVE = 'active', _('Active'),
#         CANCELLED = 'cancelled', _('Cancelled'),
#         DELIVERED = 'delivered', _('Delivered'),
#         PAUSED = 'paused', _('Paused'),
#         READY = 'ready', _('Ready'),
#         REVERTED = 'reverted', _('Reverted')

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="indsutry_jobs")
#     installer_name = models.CharField(max_length=255)
#     activity_id = models.IntegerField(null=True)
#     blueprint = models.CharField(max_length=255)
#     # 이거뭐임?
#     blueprint_id = models.BigIntegerField(null=True)
#     blueprint_type_id = models.BigIntegerField(null=True)
#     completed_character_id = models.IntegerField(null=True)
#     completed_data = models.DateTimeField(null=True)
#     cost = models.DecimalField(max_digits=13, decimal_places=4, null=True)
#     duration = models.IntegerField(null=True)
#     end_date = models.DateTimeField(null=True)
#     facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
#     installer_id = models.IntegerField(null=True)
#     job_id = models.IntegerField(null=True)
#     licensed_runs = models.IntegerField(null=True)
#     pause_date = models.DateTimeField(null=True)
#     probability = models.FloatField(null=True)
#     product_type_id = models.IntegerField(null=True)
#     runs = models.IntegerField(null=True)
#     start_date = models.DateTimeField(null=True)
#     station_id = models.BigIntegerField(null=True)
#     status = models.CharField(
#         max_length=10,
#         choices=Status.choices
#     )
#     successful_runs = models.IntegerField(null=True)

#     objects = IndustryJobManager()