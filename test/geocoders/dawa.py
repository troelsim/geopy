# -*- coding: utf-8 -*-
import unittest
from geopy import Point

from geopy.compat import u
from geopy.geocoders import Dawa
from test.geocoders.util import GeocoderTestBase, env

class DawaTestCase(GeocoderTestBase):
    @classmethod
    def setUpClass(cls):
        cls.geocoder = Dawa(
            scheme='http',
            timeout=20,
        )

    def test_geocode(self):
        self.geocode_run(
            {'query': u"Prins Jørgens Gård 1, 1218 København"},
            {'latitude': 55.6768, 'longitude': 12.5799}
        )

    def test_reverse(self):
        self.reverse_run(
            {"query": Point(55.6768, 12.5799)},
            {'latitude': 55.6768, 'longitude': 12.5799}
        )

    def test_no_results(self):
        self.geocode_run(
            {'query': u"Paradisæblevej 111, Andeby"},
            {}, expect_failure=True
        )

    def test_many_resuults(self):
        self.geocode_run(
            {'query': u"Viborgvej", 'exactly_one': False},
            {}
        )

