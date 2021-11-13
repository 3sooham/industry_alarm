from django.db import models
from django.conf import settings

class IndustryJobs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="indsutry_jobs")

    activity_id = models.IntegerField()
    blueprint_id = models.BigIntegerField()
    blueprint_type = models.BigIntegerField()
    completed_character_id = models.IntegerField()
    completed_data = models.DateTimeField()
    cost = models.DecimalField(max_digits=13, deciaml_places=4)
    duration = models.IntegerField()
    end_date = models.DateTimeField()
    facility_id = models.BigIntegerField()
    job_id = models.IntegerField()
    licensed_runs = models.IntegerField()
    output_location_id = models.BigIntegerField()
    pause_date = models.DateTimeField()
    probability = models.IntegerField()
    product_type_id = models.IntegerField()
    runs = models.IntegerField()
    start_date = models.DateTimeField()
    station_id = models.BigIntegerField()
    status = models.CharField(max_length)
    successful_runs = models.IntegerField()
