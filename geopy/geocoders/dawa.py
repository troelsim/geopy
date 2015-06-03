"""
:class:`.Dawa` is the 'Denmark's Addresses Web API' geocoder.
"""
from geopy import Location
from geopy.geocoders.base import Geocoder, DEFAULT_SCHEME, DEFAULT_TIMEOUT
from geopy.compat import urlencode

__all__ = ('Dawa',)


class Dawa(Geocoder):
    """
    Geocoder using the Dawa (Denmark's Addresses Web API / Danmarks Adressers Web API).
    Documentation at https://dawa.aws.dk
    Currently tested on cPython 2.7.6
    Tends to fail when using the (default) 'https' scheme, so use by.

    Usage:

        >>> from geopy.geocoders import Dawa
        >>> geocoder = Dawa(scheme='http')
        >>> geocoder.geocode("Harald Jensens Plads")
        Location((56.1440727139, 10.1901302108, 0.0))
        >>> geocoder.geocode("Banegaardspladsen, Aarhus", exactly_one=False)
       [Location((56.1503632165, 10.2046199686, 0.0)),
       Location((56.1501799711, 10.2038763154, 0.0)),
       Location((56.1501588186, 10.2037417209, 0.0)),
       Location((56.1501420977, 10.2036133823, 0.0)),
       ...]
    """
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