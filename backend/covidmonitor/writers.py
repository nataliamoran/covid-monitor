import datetime
import threading
import time

import pandas as pd
from .serializers import *

import logging

logger = logging.getLogger(__name__)
STEP = 3000


class Writer:
    def write_date(self, objects_list, internal_combined_key_list):
        logger.debug(f'Deleting from DB items with existing keys')
        all_queryset_after = CovidMonitorDate.objects.all()
        count = 0
        for i in range(0, len(internal_combined_key_list), STEP):
            deleted, _ = (all_queryset_after
                          .filter(internal_combined_key__in=internal_combined_key_list[i:i + STEP])
                          .delete())
            count += deleted
        logger.debug(f'Deleted {count} records from DB, now bulk creating')
        CovidMonitorDate.objects.bulk_create(objects_list)
        logger.debug(f'Done creating')

    def process_data(self, df, file_type, title):
        raise NotImplementedError


class SeriesWriter(Writer):
    def __init__(self, covid_monitor_df, file_type, title):
        super().__init__()
        self.process_data(covid_monitor_df, file_type, title)

    def process_data(self, df, file_type, title):
        # Insert data
        if file_type == 1:
            dates = df.columns.tolist()[5:]
        else:
            dates = df.columns.tolist()[12:]
        items = list()
        internal_combined_key_list = list()
        for index, row in df.iterrows():
            if file_type == 1:
                country = row["Country/Region"]
                province_state = row["Province/State"]
            else:
                country = row["Country_Region"]
                province_state = row["Province_State"]
            combined_key = row["Combined_Key"] if "Combined_Key" in df.columns.tolist() else None

            dates_count = len(dates)
            logger.debug(f'Beginning processing {dates_count} records from index {index}/{len(df)}')

            for date in dates:
                try:
                    val = int(row[date])
                    date_to_write = datetime.datetime.strptime(date, "%m/%d/%y").date()
                    internal_combined_key = (f"{title}&{date_to_write}&"
                                             f"{country}&{province_state}&"
                                             f"{row['Admin2'] if 'Admin2' in df.columns.tolist() else 'nan'}")
                    date_data = CovidMonitorDate(
                        number=val, title=title, date=date_to_write, country=country,
                        province_state=province_state, combined_key=combined_key,
                        internal_combined_key=internal_combined_key)
                    items.append(date_data)
                    internal_combined_key_list.append(internal_combined_key)
                except ValueError:
                    continue
        self.write_date(items, internal_combined_key_list)


class DailyWriter(Writer):
    def __init__(self, covid_monitor_df, file_type, date):
        super().__init__()
        self.process_data(covid_monitor_df, file_type, date)

    def process_data(self, df, file_type, date):
        items = []
        internal_combined_key_list = []
        for index, row in df.iterrows():
            combined_key = None
            if file_type == 4:
                combined_key = row["Combined_Key"]
            for title in ["Confirmed", "Deaths", "Recovered", "Active"]:
                try:
                    int(row[title])
                    internal_combined_key = f"{title.lower()}&{date}&" \
                                            f"{row['Country_Region']}&{row['Province_State']}&" \
                                            f"{row['Admin2'] if 'Admin2' in df.columns.tolist() else 'nan'}"
                    date_data = CovidMonitorDate(
                        title=title.lower(),
                        date=date, country=row["Country_Region"],
                        province_state=row["Province_State"],
                        combined_key=combined_key,
                        number=row[title],
                        internal_combined_key=internal_combined_key,
                    )
                    internal_combined_key_list.append(internal_combined_key)
                    items.append(date_data)
                except ValueError:
                    continue
        self.write_date(items, internal_combined_key_list)
