from rest_framework.response import Response
from .serializers import *
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import viewsets, status
import datetime
import pandas as pd
from .csv_verfier import Verifier
from .writers import SeriesWriter, DailyWriter
from rest_framework.decorators import action


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
        DailyWriter(covid_monitor_df, file_type, datetime.datetime.strptime(file_name.split(".")[0], "%m-%d-%Y").date())
        return Response(status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['post'], url_name='filter_dates')
    def filter_dates(self, request):
        queryset = CovidMonitorDate.objects.all()
        # filter dates per request
        if len(request.data["titles"]) > 0:
            queryset = queryset.filter(title__in=request.data["titles"], )
        if len(request.data["countries"]) > 0:
            queryset = queryset.filter(country__in=request.data["countries"], )
        if len(request.data["provinces_states"]) > 0:
            queryset = queryset.filter(province_state__in=request.data["provinces_states"], )
        if len(request.data["combined_keys"]) > 0:
            queryset = queryset.filter(combined_key__in=request.data["combined_keys"], )
        if len(request.data["date_from"]) > 0:
            try:
                date_from = datetime.datetime.strptime(request.data["date_from"], "%m/%d/%y").date()
                queryset = queryset.filter(date__gte=date_from, )
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if len(request.data["date_to"]) > 0:
            try:
                date_to = datetime.datetime.strptime(request.data["date_to"], "%m/%d/%y").date()
                queryset = queryset.filter(date__lte=date_to, )
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        # return filtered dates
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True) if page is not None \
            else self.get_serializer(queryset, many=True)
        if request.data["format"] == "JSON":  # return JSON
            return Response(serializer.data) if page is None else self.get_paginated_response(serializer.data)
        elif request.data["format"] == "CSV":  # return CSV
            data_df = pd.DataFrame(serializer.data)
            data_csv = data_df.to_csv(index=False)
            return Response(data_csv)
        return Response(status=status.HTTP_400_BAD_REQUEST)
