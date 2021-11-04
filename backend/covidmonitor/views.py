from rest_framework.response import Response
from .serializers import *
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import viewsets, status
import datetime
import pandas as pd
from .csv_verfier import Verifier
from .writers import SeriesWriter

class CsrfExemptSessionAuthentication(SessionAuthentication):
    # from https://stackoverflow.com/questions/30871033/django-rest-framework-remove-csrf
    def enforce_csrf(self, request):
        return





class DateView(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = CovidMonitorDate.objects.all()
    serializer_class = CovidMonitorDateSerializer

    def create(self, request, *args, **kwargs):
        try:
            csv_file = request.FILES['csv_file']
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        covid_monitor_df = pd.read_csv(csv_file)
        file_name = request.FILES['csv_file'].name
        verifier = Verifier()
        file_type = verifier.confirm_valid_csv(file_name, covid_monitor_df)
        if file_type == -1:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif file_type == 1 or file_type == 2:
            SeriesWriter(covid_monitor_df, file_type, verifier.time_series_type(file_name))
            return Response(status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = CovidMonitorDate.objects.all()
        titles = request.data["titles"]
        countries = request.data["countries"]
        provinces_states = request.data["provinces_states"]
        combined_keys = request.data["combined_keys"]
        date_from = datetime.datetime.strptime(request.data["date_from"], "%m/%d/%y").date()
        date_to = datetime.datetime.strptime(request.data["date_to"], "%m/%d/%y").date()

        queryset = queryset.filter(date__gte=date_from, date__lte=date_to, )
        if len(titles) > 0:
            queryset = queryset.filter(title__in=titles, )
        if len(countries) > 0:
            queryset = queryset.filter(country__in=countries, )
        if len(provinces_states) > 0:
            queryset = queryset.filter(province_state__in=provinces_states, )
        if len(combined_keys) > 0:
            queryset = queryset.filter(combined_key__in=combined_keys, )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
