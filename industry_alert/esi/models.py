from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# 클래스명 단수로
# 이름 붙이는 거는 불려오는곳에서 이름이 얼마나 자연스러운지가 중요함
class IndustryJob(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active'),
        CANCELLED = 'cancelled', _('Cancelled'),
        DELIVERED = 'delivered', _('Delivered'),
        PAUSED = 'paused', _('Paused'),
        READY = 'ready', _('Ready'),
        REVERTED = 'reverted', _('Reverted')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="indsutry_jobs")
    activity_id = models.IntegerField(null=True)
    blueprint_id = models.BigIntegerField(null=True)
    blueprint_location_id = models.BigIntegerField(null=True)
    blueprint_type_id = models.BigIntegerField(null=True)
    completed_character_id = models.IntegerField(null=True)
    completed_data = models.DateTimeField(null=True)
    cost = models.DecimalField(max_digits=13, decimal_places=4, null=True)
    duration = models.IntegerField(null=True)
    end_date = models.DateTimeField(null=True)
    facility_id = models.BigIntegerField(null=True)
    installer_id = models.IntegerField(null=True)
    job_id = models.IntegerField(null=True)
    licensed_runs = models.IntegerField(null=True)
    output_location_id = models.BigIntegerField(null=True)
    pause_date = models.DateTimeField(null=True)
    probability = models.FloatField(null=True)
    product_type_id = models.IntegerField(null=True)
    runs = models.IntegerField(null=True)
    start_date = models.DateTimeField(null=True)
    station_id = models.BigIntegerField(null=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices
    )
    successful_runs = models.IntegerField(null=True)

   # class StatusInJobs(models.TextChoices):
   #      ACTIVE = 'active', _('Active'),
   #      CANCELLED = 'cancelled', _('Cancelled'),
   #      DELIVERED = 'delivered', _('Delivered'),
   #      PAUSED = 'paused', _('Paused'),
   #      READY = 'ready', _('Ready'),
   #      REVERTED = 'reverted', _('Reverted')
   #
   #  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="indsutry_jobs")
   #  activity_id = models.IntegerField()
   #  blueprint_id = models.BigIntegerField()
   #  blueprint_location_id = models.BigIntegerField()
   #  blueprint_type_id = models.BigIntegerField()
   #  completed_character_id = models.IntegerField()
   #  completed_data = models.DateTimeField()
   #  cost = models.DecimalField(max_digits=13, decimal_places=4)
   #  duration = models.IntegerField()
   #  end_date = models.DateTimeField()
   #  facility_id = models.BigIntegerField()
   #  installer_id = models.IntegerField()
   #  job_id = models.IntegerField()
   #  licensed_runs = models.IntegerField()
   #  output_location_id = models.BigIntegerField()
   #  pause_date = models.DateTimeField()
   #  probability = models.IntegerField()
   #  product_type_id = models.IntegerField()
   #  runs = models.IntegerField()
   #  start_date = models.DateTimeField()
   #  station_id = models.BigIntegerField()
   #  status = models.CharField(
   #      max_length=10,
   #      choices=StatusInJobs.choices
   #  )
   #  successful_runs = models.IntegerField()


