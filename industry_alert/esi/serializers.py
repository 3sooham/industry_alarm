from rest_framework import serializers
from .models import IndustryJobs

class IndustryJobsSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndustryJobs
        fields = '__all__'

    # create overide해서 bulk create/update로 생성하기
