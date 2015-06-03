"""
:class:`.Dawa` is the 'Denmark's Addresses Web API' geocoder.
"""
from geopy import Location
from geopy.geocoders.base import Geocoder, DEFAULT_SCHEME, DEFAULT_TIMEOUT
from geopy.compat import urlencode

__all__ = ('Dawa',)


class Dawa(Geocoder):
    def __init__(
            self,
            scheme=DEFAULT_SCHEME,
            domain='dawa.aws.dk',
            timeout=DEFAULT_TIMEOUT,
            proxies=None
            ):
        super(Dawa, self).__init__(scheme=scheme, timeout=timeout, proxies=proxies)
        self.domain = domain
        self.api = '%s://%s/adresser' % (self.scheme, self.domain)

    def _parse_json(self, page, exactly_one):
        results = page
        if not results:
            return

        def parse_place(place):
            location = place.get('adressebetegnelse')
            coordinates = place['adgangsadresse']['adgangspunkt']['koordinater']
            latitude = coordinates[1]
            longitude = coordinates[0]
            return Location(location, (latitude, longitude), place)

        if exactly_one:
            return parse_place(results[0])
        else:
            return [parse_place(result) for result in results]

    def reverse(self, query, exactly_one=True, timeout=None):
        pass

    def geocode(self, query, exactly_one=True, timeout=None):
        params = {
            'q': self.format_string % query
        }
        url = "?".join((self.api, urlencode(params)))
        return self._parse_json(
            self._call_geocoder(url), exactly_one
        )