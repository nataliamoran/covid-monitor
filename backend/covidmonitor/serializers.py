from .models import *
from rest_framework import serializers


class CovidMonitorDateSerializer(serializers.ModelSerializer):
    #def __init__(self, *args, **kwargs):
    #    many = kwargs.pop('many', True)
    #    super(CovidMonitorDateSerializer, self).__init__(many=many, *args, **kwargs)


    class Meta:
        model = CovidMonitorDate()
        fields = ['id', 'title', 'date', 'country', 'province_state',
                  'number', 'created_at', 'updated_at']

