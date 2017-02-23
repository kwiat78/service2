import json

from orient import sort
from map import Map

map_in = 'map.json'
map_out = 'map2.json'
m = Map()
m.from_json(json.load(open(map_in, 'r')))

streets = {}
for idx, point in enumerate(m.points):
    for s in point.streets:
        if s in streets:
            streets[s].append(idx)
        else:
            streets[s] = [idx]
streets = {x: streets[x] for x in streets if len(streets[x]) > 3}


Y = {}
E = set()
for street in streets:
    st = streets[street]
    w = sort(m, st[0], st[1:])
    # for idx in range(len(w)-1):
    #     E.add((w[idx][1], w[idx+1][1]))
    Y[street] = [ww[1] for ww in w]

print(Y)

# ME = [[
#         {'latitude': m.get_point(ei[0]).latitude, 'longitude':m.get_point(ei[0]).longitude},
#         {'latitude': m.get_point(ei[1]).latitude, 'longitude':m.get_point(ei[1]).longitude}
#       ] for ei in E]
# json.dump(ME, open(map_out, 'w'))
