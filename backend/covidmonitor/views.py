from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import viewsets, status

import pandas as pd

class CsrfExemptSessionAuthentication(SessionAuthentication):
    # from https://stackoverflow.com/questions/30871033/django-rest-framework-remove-csrf
    def enforce_csrf(self, request):
        return


class DateView(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = CovidMonitorDate.objects.all()
    serializer_class = CovidMonitorDateSerializer

    def create(self, request, *args, **kwargs):
        csv_file = request.FILES['csv_file']
        covid_monitor_df = pd.read_csv(csv_file)
