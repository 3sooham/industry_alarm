from rest_framework import serializers
from .models import IndustryJob

class IndustryJobListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        print("in serializer validated_data = ", validated_data)
        # 먼저 유저에 대해서 잡이 있는지 확인
        # 잡이 있으면 먼저 없어진 인더 잡들 지우고 update_or_create
        # 잡이 없으면 create
        industry_jobs = [IndustryJob(**item) for item in validated_data]
        print("in serializer industry_jobs =", industry_jobs)

        res = IndustryJob.objects.bulk_create(industry_jobs)
        print("in serializer res = res")
        return res

    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        print("in serializer update")
        print("in serializer update instance=", instance)
        print("in serializer update validated_data=", validated_data)
        job_mapping = {job.id: job for job in instance}
        data_mapping = {item['id']: item for item in validated_data}
        print("in serializer update job_mapping=", job_mapping)
        print("in serializer update data_mapping=", data_mapping)
        # Perform creations and updates
        ret = []
        for job_id, data in data_mapping.items():
            industry_job = job_mapping.get(job_id, None)
            # job 없으면 생성
            if industry_job is None:
                ret.append(self.child.create(data))
            # 있으면 업데이트
            else:
                ret.append(self.child.update(industry_job, data))

        # Perform deletions.
        for job_id, job in job_mapping.items():
            if job_id not in data_mapping:
                job.delete()

        return ret

        def validate(self, attr):
            print("in validate")
            # 이거는 request 전부가 serializer로 감
            # self.context['view'].action 이거로 더 자세한 정보 볼 수 있음
            # 어떤 함수 불러온지 알 수 있기 때문임
            attr['user'] = self.context['user']
            print(attr)
            return attr

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
        fields = ['id', 'user', 'activity_id', 'blueprint_id', 'blueprint_location_id', 'blueprint_type_id',
                  'completed_character_id', 'completed_date', 'cost',
                  'duration', 'end_date', 'facility_id', 'installer_id', 'job_id', 'licensed_runs', 'output_location_id',
                  'pause_date', 'probability', 'product_type_id', 'runs', 'start_date', 'station_id', 'status',
                  'successful_runs']