from .models import *
from rest_framework import serializers


class CovidMonitorDateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CovidMonitorDate
        fields = ['id', 'title', 'date', 'country', 'province_state',
                  'number', 'created_at', 'updated_at']

