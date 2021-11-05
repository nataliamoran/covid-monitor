import json
import os
from typing import Dict

from django.test import TestCase, Client
from rest_framework.reverse import reverse

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TIME_SERIES_CONFIRMED_GLOBAL_PATH = f'{DIR_PATH}/test_files/time_series_covid19_confirmed_global.csv'
TIME_SERIES_CONFIRMED_US_PATH = f'{DIR_PATH}/test_files/time_series_covid19_confirmed_US.csv'


class MonitorClient:
    def __init__(self):
        self.client = Client()

    def date_list(self):
        return self.client.get(reverse('dates-list'))

    def date_filter_list(self, filters: Dict):
        return self.client.post(reverse('dates-filter_dates'), json.dumps(filters), content_type='application/json')

    def date_create(self, csv_path: str):
        fp = open(csv_path)
        return self.client.post(reverse('dates-list'), {'csv_file': fp})


class TestMonitor(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cli = MonitorClient()

    def test__upload_time_series_global__green(self):
        # arrange
        # act
        dates_before = self.cli.date_list()
        res = self.cli.date_create(TIME_SERIES_CONFIRMED_GLOBAL_PATH)
        dates_after = self.cli.date_list()
        # assert
        self.assertEquals(201, res.status_code)
        self.assertEquals(0, len(dates_before.data))
        self.assertEquals(1944, len(dates_after.data))

    def test__content_time_series_global__green(self):
        # arrange
        # act
        self.cli.date_create(TIME_SERIES_CONFIRMED_GLOBAL_PATH)
        dates_after = self.cli.date_list()
        # assert
        self.assertEquals(0, dates_after.data[0]['number'])
        self.assertEquals("confirmed", dates_after.data[0]['title'])
        self.assertEquals('2020-01-23', dates_after.data[0]['date'])
        self.assertEquals("Afghanistan", dates_after.data[0]['country'])
        self.assertEquals('nan', dates_after.data[0]['province_state'])
        self.assertEquals(None, dates_after.data[0]['combined_key'])

    def test__filter_countries__green(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": ["Algeria", "US"],
            "provinces_states": [],
            "combined_keys": [],
            "date_from": "10/30/21",
            "date_to": "10/31/21",
            "format": "JSON"
        }
        self.cli.date_create(TIME_SERIES_CONFIRMED_GLOBAL_PATH)
        self.cli.date_create(TIME_SERIES_CONFIRMED_US_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(200, res.status_code)
        self.assertEquals(8, len(res.data))
