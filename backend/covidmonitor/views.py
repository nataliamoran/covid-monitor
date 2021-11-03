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
        for item in dates_json_list:
            # save a new order to the db
            serializer = self.get_serializer(data=item)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_201_CREATED)

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
            for date in dates:
                date_data = {
                    "title": title,
                    "date": datetime.datetime.strptime(date, "%m/%d/%y"),
                    "country": country,
                    "province_state": province_state,
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
