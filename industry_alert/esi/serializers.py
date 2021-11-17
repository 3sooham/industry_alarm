from rest_framework import serializers
from .models import IndustryJob

class IndustryJobListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        print("in serializer validated_data = ", validated_data)
        industry_jobs = [IndustryJob(**item) for item in validated_data]
        print("in serializer industry_jobs =", industry_jobs)
        return IndustryJob.objects.bulk_create(industry_jobs)

    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        job_mapping = {job.id: job for job in instance}
        data_mapping = {item['id']: item for item in validated_data}

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

        # # Perform deletions.
        # for book_id, book in book_mapping.items():
        #     if book_id not in data_mapping:
        #         book.delete()

        return ret

# class IndustryJobSerializer(serializers.ListSerializer):
#     def update(self, instance, validated_data):
#         # Maps for id->instance and id->data item.
#         job_mapping = {job.id: job for job in instance}
#         data_mapping = {item['id']: item for item in validated_data}
#
#         # Perform creations and updates
#         ret = []
#         for job_id, data in data_mapping.items():
#             industry_job = job_mapping.get(job_id, None)
#             # job 없으면 생성
#             if industry_job is None:
#                 ret.append(self.child.create(data))
#             # 있으면 업데이트
#             else:
#                 ret.append(self.child.update(industry_job, data))
#
#         # # Perform deletions.
#         # for book_id, book in book_mapping.items():
#         #     if book_id not in data_mapping:
#         #         book.delete()
#
#         return ret

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

    # bulk_create 테스트
    def bulk_create(self, validated_data):
        print(validated_data)
        print(type(validated_data))