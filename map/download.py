import requests
import json

from map import Map

SERVICE = 'http://service2-kwiat78.rhcloud.com'
API = '{}/api'.format(SERVICE)
TRACKS_URL = "{}/tracks".format(API)
MAP_FILE = "map.json"

my_map = Map()

try:
    f = open(MAP_FILE, "r")
    map_json = json.load(f)
    my_map.from_json(map_json)
except FileNotFoundError:
    pass
except ValueError:
    pass

# DOWNLOAD
tracks = requests.get(TRACKS_URL).json()
limit = 1
current = 0

for t in tracks:
    params = requests.get("{}/{}/params".format(TRACKS_URL, t))
    processed = params.json()["processed"]
    if not processed:
        xx = requests.get("{}/{}/only_intersections".format(TRACKS_URL, t))
        if xx.status_code == 200:
            ox = xx.json()
            requests.get("{}/{}/process".format(TRACKS_URL, t))
            current += 1

            for point, point2 in zip(ox[:-1], ox[1:]):
                my_map.add_point(point)
                my_map.add_point(point2)
                my_map.add_edge(point, point2)
        else:
            pass
    if current == limit:
        break
with open(MAP_FILE, "w") as f:
    json.dump(my_map.to_json(), f)
