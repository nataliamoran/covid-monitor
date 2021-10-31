import json
from typing import Dict

from django.test import TestCase, Client
from rest_framework.reverse import reverse


class MonitorClient:
    def __init__(self):
        self.client = Client()


class TestMonitor(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cli = MonitorClient()

    def test_example(self):
        pass
