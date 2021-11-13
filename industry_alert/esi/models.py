from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# d
class IndustryJobs(models.Model):
    class StatusInJobs(models.TextChoices):
        ACTIVE = 'active', _('Active'),
        CANCELLED = 'cancelled', _('Cancelled'),
        DELIVERED = 'delivered', _('Delivered'),
        PAUSED = 'paused', _('Paused'),
        READY = 'ready', _('Ready'),
        REVERTED = 'reverted', _('Reverted')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="indsutry_jobs")
    activity_id = models.IntegerField()
    blueprint_id = models.BigIntegerField()
    blueprint_location_id = models.BigIntegerField()
    blueprint_type_id = models.BigIntegerField()
    completed_character_id = models.IntegerField()
    completed_data = models.DateTimeField()
    cost = models.DecimalField(max_digits=13, decimal_places=4)
    duration = models.IntegerField()
    end_date = models.DateTimeField()
    facility_id = models.BigIntegerField()
    installer_id = models.IntegerField()
    job_id = models.IntegerField()
    licensed_runs = models.IntegerField()
    output_location_id = models.BigIntegerField()
    pause_date = models.DateTimeField()
    probability = models.IntegerField()
    product_type_id = models.IntegerField()
    runs = models.IntegerField()
    start_date = models.DateTimeField()
    station_id = models.BigIntegerField()
    status = models.CharField(
        max_length=10,
        choices=StatusInJobs.choices
    )
    successful_runs = models.IntegerField()


