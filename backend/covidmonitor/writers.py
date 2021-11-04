import datetime
from .serializers import *


class Writer:
    def write_date(self, dates_json_list):
        bulk_list = []
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
                    bulk_list.append(obj)
            except CovidMonitorDate.DoesNotExist:
                obj = CovidMonitorDate(**date_item)
                bulk_list.append(obj)
                obj.save()


class SeriesWriter(Writer):
    def __init__(self, covid_monitor_df, file_type, title):
        self.write_series(covid_monitor_df, file_type, title)

    def write_series(self, df, file_type, title):
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


class DailyWriter(Writer):
    def write_daily(self, df, file_name, file_type):
        date = datetime.datetime.strptime(file_name, "%m/%d/%Y").date()
        dates_json_list = []
        for index, row in df.iterrows():
            if file_type == 1:
                country = row["Country/Region"]
                province_state = row["Province/State"]
            else:
                country = row["Country_Region"]
                province_state = row["Province_State"]
            combined_key = row["Combined_Key"] if "Combined_Key" in df.columns.tolist() else None
            titles = ["Confirmed", "Deaths", "Recovered", "Active"]
            if "Combined_Key" in df.columns.tolist():
                titles.append("Combined_Key")
            for title in ["Confirmed", "Deaths", "Recovered", "Active"]:
                date_data = {
                    "title": title,
                    "date": date,
                    "country": country,
                    "province_state": province_state,
                    "combined_key": combined_key,
                    "number": row[title]
                }
                dates_json_list.append(date_data)
        self.write_date(dates_json_list)
