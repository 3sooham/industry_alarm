from rest_framework import serializers
from .models import IndustryJobs

class IndustryJobsSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndustryJobs
        fields = ['activity_id', 'blueprint_id', 'blueprint_location_id', 'blueprint_type_id', 'cost',
                  'duration', 'end_date', 'facility_id', 'installer_id', 'job_id', 'licensed_runs', 'output_location_id',
                  'probability', 'product_type_id', 'runs', 'start_date', 'station_id', 'status']

    def validate_status(self, value):
        status_choice_class = self.Meta.model.StatusInJobs
        try:
            choice = getattr(status_choice_class, value)
        except AttributeError:
            raise ValidationError('no such choices')
        return choice