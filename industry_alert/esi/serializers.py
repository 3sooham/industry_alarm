from rest_framework import serializers
from .models import IndustryJob

class IndustryJobListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        print("in serializer validated_data = ", validated_data)
        print("in serializer validated_data type = ", type(validated_data))
        # 먼저 유저에 대해서 잡이 있는지 확인
        instance = IndustryJob.objects.filter(user=validated_data[0]['user'])
        if instance.exist():
            # instance를 job_id를 key로 정리
            job_mapping = {job.job_id: job for job in instance}
            # validated_data를 job_id를 키로 정리
            data_mapping = {item['job_id']: item for item in validated_data}
            ret = []
            need_create = []
            for job_id, data in data_mapping.items():
                # validated_data에서 job_id를 가져와서 이게 instance에 있는지 확인
                industry_job = job_mapping.get(job_id, None)
                # job 없으면 새로 생긴거니 생성
                if industry_job is None:
                    need_create.append(industry_job)
                    # ret.append(self.child.create(data))
                # job이 있으면 업데이트
                else:
                    ret.append(self.child.update(industry_job, data))
                    # bulk update 사용

            # validated_data이거 dic인지 list인지 확인해야함
            industry_jobs = [IndustryJob(**item) for item in need_create]
            IndustryJob.objects.bulk_create(industry_jobs)

            # Perform deletions.
            # 이미 있는 잡이 새로 불러온 job에 없으면 완료되서 사라진거니 삭제해줌
            for job_id, job in job_mapping.items():
                if job_id not in data_mapping:
                    job.delete()

            return ret

        # 유저에 대해서 잡이 없으면 create
        industry_jobs = [IndustryJob(**item) for item in validated_data]
        res = IndustryJob.objects.bulk_create(industry_jobs)
        return res

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
        attr['user'] = self.context['user']
        return attr