from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import viewsets, status
import datetime
import pandas as pd

TIME_SERIES_COLUMNS = [["Province/State", "Country/Region"], ["Province_State", "Country_Region"]]
DAILY_REPORTS_COLUMNS = ["Province_State", "Country_Region", "Confirmed", "Deaths", "Recovered", "Active"]
SERIES_OPTS = ["deaths", "confirmed", "active", "recovered"]
SERIES_TYPE_ONE = 1
SERIES_TYPE_TWO = 2
DAILY = 3


def confirm_columns(df, columns):
    if all(x in df.columns.tolist() for x in columns):
        return True
    return False


def confirm_valid_csv(file_name, df):
    # We first check if we have a daily or time series file
    is_daily_file = False
    try:
        date1 = datetime.datetime.strptime(file_name, "%m-%d-%Y").date()
        is_daily_file = True
    except ValueError:
        is_daily_file = False
    if is_daily_file and confirm_columns(df, DAILY_REPORTS_COLUMNS):
        return DAILY
    elif not is_daily_file and confirm_columns(df, TIME_SERIES_COLUMNS[0]):
        return SERIES_TYPE_ONE
    elif not is_daily_file and confirm_columns(df, TIME_SERIES_COLUMNS[1]):
        return SERIES_TYPE_TWO
    else:  # csv is not valid
        return -1


class CsrfExemptSessionAuthentication(SessionAuthentication):
    # from https://stackoverflow.com/questions/30871033/django-rest-framework-remove-csrf
    def enforce_csrf(self, request):
        return


class DateView(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = CovidMonitorDate.objects.all()
    serializer_class = CovidMonitorDateSerializer

    def write_date(self, dates_json_list):
        for date_item in dates_json_list:
            try:
                obj = CovidMonitorDate.objects.get(title=date_item["title"],
                                                   date=date_item["date"],
                                                   country=date_item["country"],
                                                   province_state=date_item["province_state"],
                                                   combined_key=date_item["combined_key"])
                if obj.number != date_item["number"]:
                    for key, value in date_item.items():
                        setattr(obj, key, value)
                    obj.save()
            except CovidMonitorDate.DoesNotExist:
                obj = CovidMonitorDate(**date_item)
                obj.save()

    def write_series(self, df, file_name, file_type):
        lower_file = file_name.lower()
        if "confirmed" in lower_file:
            title = "confirmed"
        elif "deaths" in lower_file:
            title = "deaths"
        elif "recovered" in lower_file:
            title = "recovered"
        elif "active" in lower_file:
            title = "active"
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        dates_json_list = []
        if file_type == 1:
            dates = df.columns.tolist()[5:]
        else:
            dates = df.columns.tolist()[12:]
        for index, row in df.iterrows():
            if file_type == 1:
                country = row["Country/Region"]
                province_state = row["Province/State"]
            else:
                country = row["Country_Region"]
                province_state = row["Province_State"]
            combined_key = row["Combined_Key"] if "Combined_Key" in df.columns.tolist() else None
            for date in dates:
                date_data = {
                    "title": title,
                    "date": datetime.datetime.strptime(date, "%m/%d/%y").date(),
                    "country": country,
                    "province_state": province_state,
                    "combined_key": combined_key,
                    "number": row[date]
                }
                dates_json_list.append(date_data)
        self.write_date(dates_json_list)

    def create(self, request, *args, **kwargs):
        try:
            csv_file = request.FILES['csv_file']
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        covid_monitor_df = pd.read_csv(csv_file)
        file_name = request.FILES['csv_file'].name
        file_type = confirm_valid_csv(file_name, covid_monitor_df)
        if file_type == -1:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif file_type == SERIES_TYPE_ONE or file_type == SERIES_TYPE_TWO:
            self.write_series(covid_monitor_df, file_name, file_type)
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
            queryset = queryset.filter(title__in=titles,)
        if len(countries) > 0:
            queryset = queryset.filter(country__in=countries,)
        if len(provinces_states) > 0:
            queryset = queryset.filter(province_state__in=provinces_states,)
        if len(combined_keys) > 0:
            queryset = queryset.filter(combined_key__in=combined_keys,)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
