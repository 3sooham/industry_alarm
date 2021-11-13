from rest_framework import serializers
from .models import IndustryJobs

class IndustryJobsSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndustryJobs

    # bulk create로 생성하기
