from rest_framework import serializers
from .models import IndustryJob

# atomic
from django.db import transaction


class IndustryJobListSerializer(serializers.ListSerializer):
    # https://wikidocs.net/21054
    # 이거를 그냥 하면 이 함수를 불러올때마다 스택에 올렸다 내렸다하니
    # @staticmethod로 힙에 올려버리기
    # 지금은 작아서 상관없는데 커지면 유의미해짐
    @staticmethod
    def set_status(job, new_status):
        job.status = new_status
        return job

    # atomic allows us to create a block of code within which the atomicity on the database is guaranteed.
    # 이 함수는 atomic하게 transaction처리함
    # https://docs.djangoproject.com/en/3.2/topics/db/transactions/#order-of-execution
    @transaction.atomic
    def create(self, validated_data):
        # print("in serializer validated_data = ", validated_data)

        # 이거 validated_data가 비어이씅면 어떻게해야함?

        # 유저에 대해서 저장된 잡이 있는지 확인
        # filter에서는 db hit 안함
        # 이거 찍어보면 queryset 오브젝트 나오고 하나 get하기전에는 db에서 값을 가져오지 않음
        # https://docs.djangoproject.com/en/3.2/ref/models/querysets/
        # evaluate할때만 db랑 통신함

        # 밑처럼 하지말고 self.context['user'] 로 instance가져오기
        # instance = IndustryJob.objects.filter(user=validated_data[0]['user'])
        # print(self.context['user'])
        instance = IndustryJob.objects.filter(user=self.context['user'])
        # 유저에 대해서 저장된 잡이 있으면
        if instance.exists():
            # 기존에 존재하는 job들을 job_id를 key로 정리
            # 여기서 iterate하니  db hit 하는거임
            job_mapping = {job.job_id: job for job in instance}
            # 새로 받아온 job들을 job_id를 키로 정리
            data_mapping = {item['job_id']: item for item in validated_data}

            # 새로 받아온 job이 db에 저장되어 있는지 확인하고 없으면 생성
            need_create = [
                IndustryJob(**data) for job_id, data in data_mapping.items() if job_mapping.get(job_id) is None
            ]
            # 이거 []들어가면 실행안하고 끝나서 if need_crate: 이렇게 안해도됨
            IndustryJob.objects.bulk_create(need_create)

            # 새로 받아온 job이 db에 저장되어 있고 status가 변경 됐으면 update 해줌
            # 이거 staticmethod는 불러올때 크래스명
            need_update = [
                IndustryJobListSerializer.set_status(job, data_mapping[job_id]['status']) for job_id, job in job_mapping.items()
                if job_id in data_mapping.keys() and job.status != data_mapping[job_id]['status']
            ]
            IndustryJob.objects.bulk_update(need_update, ['status'])

            # 이미 있는 잡이 새로 불러온 job에 없으면 완료되서 사라진거니 삭제해줌
            # 이거 python gc가 reference기반이어서 아래에서 더이상 안쓰면 알아서 지워줌
            # 아래 리스트 만들면서 job.delete() 실행하고 다음줄 내려가면서 메모리에서 날아감
            [job.delete() for job_id, job in job_mapping.items() if job_id not in data_mapping]

            # bulk_create, bulk_update의 리턴값을 넘겨주지말고 그냥 이렇게 해도됨
            # 실제로 생성된 것도 아니니까 생성전 데이터만 넣어주기
            ret = [*need_create, *need_update]
            if ret:
                return ret
            return validated_data

        # 유저에 대해서 잡이 없으면 create
        industry_jobs = [IndustryJob(**item) for item in validated_data]
        return IndustryJob.objects.bulk_create(industry_jobs)

class IndustryJobSerializer(serializers.ModelSerializer):
    # 이거 id 기본으로는 read_only여가지고 이렇게 해줘야함
    # id = serializers.IntegerField()
    completed_character_id = serializers.IntegerField(required=False)
    completed_date = serializers.DateTimeField(required=False)
    cost = serializers.DecimalField(max_digits=13, decimal_places=4, required=False)
    licensed_runs = serializers.IntegerField(required=False)
    pause_date = serializers.DateTimeField(required=False)
    probability = serializers.FloatField(required=False)
    product_type_id = serializers.IntegerField(required=False)
    successful_runs = serializers.IntegerField(required=False)

    class Meta:
        list_serializer_class = IndustryJobListSerializer
        model = IndustryJob
        # 이거 context로 user넣어줄거라서 user일단 fields에서 뺌
        fields = ['id', 'activity_id', 'blueprint_id', 'blueprint_location_id', 'blueprint_type_id',
                  'completed_character_id', 'completed_date', 'cost',
                  'duration', 'end_date', 'facility_id', 'installer_id', 'job_id', 'licensed_runs', 'output_location_id',
                  'pause_date', 'probability', 'product_type_id', 'runs', 'start_date', 'station_id', 'status',
                  'successful_runs']

    def validate(self, attr):
        if self.context.get('user'):
            attr['user'] = self.context['user']
            return attr

        raise ValidationError