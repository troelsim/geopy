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
        self.reverse_api = '%s://%s/adgangsadresser/reverse' % (self.scheme, self.domain)

    def _parse_place(self, place):
        location = place.get('adressebetegnelse')
        if not location:  # This is not an address, try parsing it as an access address
            return self._parse_access_address(place)
        coordinates = place['adgangsadresse']['adgangspunkt']['koordinater']
        latitude = coordinates[1]
        longitude = coordinates[0]
        return Location(location, (latitude, longitude), place)

    def _parse_access_address(self, access_address):
        location = self._format_address(
            access_address['vejstykke']['navn'],
            access_address['husnr'],
            access_address['postnummer']['nr'],
            access_address['postnummer']['navn']
        )
        coordinates = access_address['adgangspunkt']['koordinater']
        latitude = coordinates[1]
        longitude = coordinates[0]
        return Location(location, (latitude, longitude), access_address)

    def _format_address(self, street, number, zip, city):
        return "%s %s, %s %s" % (street, number, zip, city)

    def _parse_json(self, page, exactly_one):
        results = page
        if not results:
            return
        if not isinstance(results, list):
            results = [results]

        if exactly_one:
            return self._parse_place(results[0])
        else:
            return [self._parse_place(result) for result in results]

    def reverse(self, query, exactly_one=True, timeout=None):
        params = {
            'x': query.longitude,
            'y': query.latitude
        }
        url = "?".join((self.reverse_api, urlencode(params)))
        return self._parse_json(
            self._call_geocoder(url, timeout=timeout), exactly_one
        )

    def geocode(self, query, exactly_one=True, timeout=None):
        params = {
            'q': self.format_string % query
        }
        url = "?".join((self.api, urlencode(params)))
        return self._parse_json(
            self._call_geocoder(url, timeout=timeout), exactly_one
        )