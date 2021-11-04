from django.db import models


class CovidMonitorDate(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    country = models.CharField(max_length=255)
    province_state = models.CharField(max_length=255, blank=True, null=True)
    combined_key = models.CharField(max_length=255, blank=True, null=True)
    number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("title", "date", "country", "province_state", "combined_key"),)

    def __str__(self):
        return self.title

