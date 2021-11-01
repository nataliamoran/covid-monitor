from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProvinceState(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=False, null=False, related_name='+')

    def __str__(self):
        return self.name


class CovidMonitorDate(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=False, null=False, related_name='+')
    province_state = models.ForeignKey(ProvinceState, on_delete=models.CASCADE, blank=False, null=False, related_name='+')
    time_series_num = models.IntegerField(blank=True, null=True)
    daily_reports_num = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

