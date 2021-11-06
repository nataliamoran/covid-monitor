import json
import os
from typing import Dict

from django.test import TestCase, Client
from rest_framework.reverse import reverse

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TIME_SERIES_CONFIRMED_GLOBAL_PATH = f'{DIR_PATH}/test_files/time_series_covid19_confirmed_global.csv'
TIME_SERIES_CONFIRMED_US_PATH = f'{DIR_PATH}/test_files/time_series_covid19_confirmed_US.csv'
DAILY_REPORT_PATH = f'{DIR_PATH}/test_files/01-01-2021.csv'
BAD_DAILY_REPORT_PATH = f'{DIR_PATH}/test_files/bad_daily_file.csv'
BAD_TIME_SERIES_CONFIRMED_GLOBAL_PATH = f'{DIR_PATH}/test_files/bad_time_series_covid19_confirmed_global.csv'
BAD_TIME_SERIES_NOTHING_US_PATH = f'{DIR_PATH}/test_files/bad_time_series_covid19_nothing_US.csv'

class MonitorClient:
    def __init__(self):
        self.client = Client()

    def date_list(self):
        return self.client.get(reverse('dates-list'))

    def date_filter_list(self, filters: Dict):
        return self.client.post(reverse('dates-filter_dates'), json.dumps(filters), content_type='application/json')

    def date_delete_all(self):
        return self.client.delete(reverse('dates-delete_all_dates'))

    def date_create(self, csv_path: str):
        fp = open(csv_path)
        return self.client.post(reverse('dates-list'), {'csv_file': fp})


class TestMonitor(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cli = MonitorClient()

    def test__bad_upload_daily_global__green(self):
        # arrange
        # act
        dates_before = self.cli.date_list()
        res = self.cli.date_create(BAD_DAILY_REPORT_PATH)
        dates_after = self.cli.date_list()
        # assert
        self.assertEquals(400, res.status_code)
        self.assertEquals(0, len(dates_before.data))
        self.assertEquals(0, len(dates_after.data))

    def test__bad_upload_series_global__green(self):
        # arrange
        # act
        dates_before = self.cli.date_list()
        res = self.cli.date_create(BAD_TIME_SERIES_CONFIRMED_GLOBAL_PATH)
        dates_after = self.cli.date_list()
        # assert
        self.assertEquals(400, res.status_code)
        self.assertEquals(0, len(dates_before.data))
        self.assertEquals(0, len(dates_after.data))

    def test__bad_upload_series_US__green(self):
        # arrange
        # act
        dates_before = self.cli.date_list()
        res = self.cli.date_create(BAD_TIME_SERIES_NOTHING_US_PATH)
        dates_after = self.cli.date_list()
        # assert
        self.assertEquals(400, res.status_code)
        self.assertEquals(0, len(dates_before.data))
        self.assertEquals(0, len(dates_after.data))

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

    def test__upload_daily_global__green(self):
        # arrange
        # act
        dates_before = self.cli.date_list()
        res = self.cli.date_create(DAILY_REPORT_PATH)
        dates_after = self.cli.date_list()
        # assert
        self.assertEquals(201, res.status_code)
        self.assertEquals(0, len(dates_before.data))
        self.assertEquals(16, len(dates_after.data))

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

    def test__content_daily__green(self):
        # arrange
        # act
        self.cli.date_create(DAILY_REPORT_PATH)
        dates_after = self.cli.date_list()
        # assert
        self.assertEquals(52513, dates_after.data[0]['number'])
        self.assertEquals("confirmed", dates_after.data[0]['title'])
        self.assertEquals('2021-01-01', dates_after.data[0]['date'])
        self.assertEquals("Afghanistan", dates_after.data[0]['country'])
        self.assertEquals('nan', dates_after.data[0]['province_state'])
        self.assertEquals("Afghanistan", dates_after.data[0]['combined_key'])

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
        self.assertEquals(12, len(res.data))

    def test__filter_titles__green(self):
        # arrange
        filter_data = {
            "titles": ["confirmed", "active"],
            "countries": [],
            "provinces_states": [],
            "combined_keys": [],
            "date_from": "01/01/21",
            "date_to": "01/01/21",
            "format": "JSON"
        }
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(200, res.status_code)
        self.assertEquals(8, len(res.data))

    def test__filter_provinces_states__green(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": [],
            "provinces_states": ["California", "Idaho"],
            "combined_keys": [],
            "date_from": "01/23/20",
            "date_to": "01/25/20",
            "format": "JSON"
        }
        self.cli.date_create(TIME_SERIES_CONFIRMED_US_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(200, res.status_code)
        self.assertEquals(6, len(res.data))

    def test__filter_combined_keys__green(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": [],
            "provinces_states": [],
            "combined_keys": ["Baldwin, Alabama, US", "Ventura, California, US"],
            "date_from": "01/23/20",
            "date_to": "01/25/20",
            "format": "JSON"
        }
        self.cli.date_create(TIME_SERIES_CONFIRMED_US_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(200, res.status_code)
        self.assertEquals(6, len(res.data))

    def test__multiple_filters__green(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": ["Afghanistan", "US"],
            "provinces_states": ["Alabama"],
            "combined_keys": ["Barbour, Alabama, US"],
            "date_from": "01/23/20",
            "date_to": "01/25/20",
            "format": "JSON"
        }
        self.cli.date_create(TIME_SERIES_CONFIRMED_US_PATH)
        self.cli.date_create(TIME_SERIES_CONFIRMED_GLOBAL_PATH)
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(200, res.status_code)
        self.assertEquals(3, len(res.data))

    def test_format__csv__green(self):
        # arrange
        filter_data = {
            "titles": ["confirmed"],
            "countries": ["Afghanistan"],
            "provinces_states": [],
            "combined_keys": [],
            "date_from": "01/01/21",
            "date_to": "01/01/21",
            "format": "CSV"
        }
        expected_res = "id,title,date,country,province_state,combined_key,number,created_at,updated_at\n" \
                       "1,confirmed,2021-01-01,Afghanistan,nan,Afghanistan,52513," \
                       "2021-11-05T14:55:24.192416-04:00,2021-11-05T14:55:24.192488-04:00\n"

        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        expected_res_replace = expected_res.replace('\n', ' ').replace('\r', '')
        res_replace = res.data.replace('\n', ' ').replace('\r', '')
        # assert
        self.assertEquals(200, res.status_code)
        self.assertEquals(expected_res_replace.split(',')[:-2], res_replace.split(',')[:-2])


    def test__bad_format_request__date_from_1__return_400(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": ["Afghanistan", "US"],
            "provinces_states": ["Alabama"],
            "combined_keys": ["Barbour, Alabama, US"],
            "date_from": "123",
            "date_to": "01/01/21",
            "format": "JSON"
        }
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(400, res.status_code)

    def test__bad_format_request__date_from_2__return_400(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": ["Afghanistan", "US"],
            "provinces_states": ["Alabama"],
            "combined_keys": ["Barbour, Alabama, US"],
            "date_from": 1,
            "date_to": "01/01/21",
            "format": "JSON"
        }
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(400, res.status_code)

    def test__bad_format_request__date_to_1__return_400(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": ["Afghanistan", "US"],
            "provinces_states": ["Alabama"],
            "combined_keys": ["Barbour, Alabama, US"],
            "date_from": "01/01/21",
            "date_to": "123",
            "format": "JSON"
        }
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(400, res.status_code)

    def test__bad_format_request__date_to_2__return_400(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": ["Afghanistan", "US"],
            "provinces_states": ["Alabama"],
            "combined_keys": ["Barbour, Alabama, US"],
            "date_from": "01/01/21",
            "date_to": 1,
            "format": "JSON"
        }
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(400, res.status_code)

    def test__bad_format_request__titles__return_400(self):
        # arrange
        filter_data = {
            "titles": "",
            "countries": ["Afghanistan", "US"],
            "provinces_states": ["Alabama"],
            "combined_keys": ["Barbour, Alabama, US"],
            "date_from": "01/01/21",
            "date_to": "01/01/21",
            "format": "JSON"
        }
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(400, res.status_code)

    def test__bad_format_request__countries__return_400(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": 1,
            "provinces_states": ["Alabama"],
            "combined_keys": ["Barbour, Alabama, US"],
            "date_from": "01/01/21",
            "date_to": "01/01/21",
            "format": "JSON"
        }
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(400, res.status_code)

    def test__bad_format_request__provinces__return_400(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": [],
            "provinces_states": "",
            "combined_keys": ["Barbour, Alabama, US"],
            "date_from": "01/01/21",
            "date_to": "01/01/21",
            "format": "JSON"
        }
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(400, res.status_code)

    def test__bad_format_request__combined_keys__return_400(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": [],
            "provinces_states": [],
            "combined_keys": 1,
            "date_from": "01/01/21",
            "date_to": "01/01/21",
            "format": "JSON"
        }
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(400, res.status_code)

    def test__bad_format_request__format_1__return_400(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": [],
            "provinces_states": [],
            "combined_keys": 1,
            "date_from": "01/01/21",
            "date_to": "01/01/21",
            "format": "test"
        }
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(400, res.status_code)

    def test__bad_format_request__format_2__return_400(self):
        # arrange
        filter_data = {
            "titles": [],
            "countries": [],
            "provinces_states": [],
            "combined_keys": 1,
            "date_from": "01/01/21",
            "date_to": "01/01/21",
            "format": 1
        }
        self.cli.date_create(DAILY_REPORT_PATH)
        # act
        res = self.cli.date_filter_list(filter_data)
        # assert
        self.assertEquals(400, res.status_code)

    def test__delete_all_dates__green(self):
        # arrange
        # act
        dates_before_addition = self.cli.date_list()
        self.cli.date_create(TIME_SERIES_CONFIRMED_GLOBAL_PATH)
        dates_after_addition = self.cli.date_list()
        res = self.cli.date_delete_all()
        dates_after_deletion = self.cli.date_list()
        # assert
        self.assertEquals(200, res.status_code)
        self.assertEquals(0, len(dates_before_addition.data))
        self.assertEquals(1944, len(dates_after_addition.data))
        self.assertEquals(0, len(dates_after_deletion.data))
