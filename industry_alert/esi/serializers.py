from rest_framework import serializers
from .models import IndustryJob

class IndustryJobsSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndustryJobs
        fields = ['activity_id', 'blueprint_id', 'blueprint_location_id', 'blueprint_type_id', 'cost',
                  'duration', 'end_date', 'facility_id', 'installer_id', 'job_id', 'licensed_runs', 'output_location_id',
                  'probability', 'product_type_id', 'runs', 'start_date', 'station_id', 'status']

    # 이거 'active' 이런게 들어가는게 아니라
    # 튜플이 들어가야함
    # IndustryJobs.objects.create(status=IndustryJobs.StatusInJobs.ACTIVE) 이렇게