from .models import *
from rest_framework import serializers


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ['id', 'name', ]


class ProvinceStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProvinceState
        fields = ['id', 'name', ]


class CovidMonitorDateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CovidMonitorDate
        fields = ['id', 'title', 'date', 'country', 'province_state',
                  'time_series_num', 'daily_reports_num',
                  'created_at', 'updated_at', ]
