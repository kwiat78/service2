import requests


class GeocodingException(BaseException):
    pass


class GoogleAPIClient(object):

    GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    SNAP_TO_ROADS_URL = 'https://roads.googleapis.com/v1/snapToRoads'

    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, location):
        response = requests.get(
            url=self.GEOCODING_URL,
            params={
                "key": self.api_key,
                "latlng": "{}, {}".format(location.latitude, location.longitude)
            }
        )
        if response.status_code == 200:
            routes = list(filter(lambda x: 'route' in x['types'], response.json()['results'][0]['address_components']))
            street = routes[0]['long_name']
            return street
        raise GeocodingException

    def snap_to_roads(self, locations):
        response = requests.get(
            url=self.SNAP_TO_ROADS_URL,
            params={
                "key": self.api_key,
                "interpolate": True,
                "path": "|".join(list(map(lambda x: "{}, {}".format(x.latitude, x.longitude), locations)))
            }
        )
        return map(lambda x: x['location'], response.json()['snappedPoints'])
