from wsgi.locations.utils.vector import dot, vector_length


class Point(object):
    def __init__(self, intersection):
        self.longitude = intersection['longitude']
        self.latitude = intersection['latitude']
        self.streets = set([intersection['street_a'], intersection['street_b']])

    def add_street(self, street):
        self.streets.add(street)

    def label(self):
        return str(self.latitude) + "___" + str(self.longitude)


class Map(object):
    def __init__(self):
        self.points = []
        self.index = {}
        self.edges = set()

    def _sort(self, idx_point, idx_points):
        point = self.points[idx_point]
        points = [self.points[idx] for idx in idx_points]

        group = [(0.0, idx_point)]
        ry = float(points[0].latitude) - float(point.latitude)
        rx = float(points[0].longitude) - float(point.longitude)

        for idx, i in zip(idx_points, points):
            dy = float(i.latitude) - float(point.latitude)
            dx = float(i.longitude) - float(point.longitude)
            alpha = 1
            if dot([rx, ry], [dx, dy]) < 0:
                alpha = -1
            re = vector_length([dx, dy]) * alpha
            group.append((re, idx))
        group.sort()
        return group

    def add_point(self, intersection):
        label = "{}___{}".format(intersection['latitude'], intersection['longitude'])
        if label in self.index:
            spoint = self.points[self.index[label]]
            spoint.add_street(intersection['street_a'])
            spoint.add_street(intersection['street_b'])
        else:
            self.points += [Point(intersection)]
            self.index[label] = len(self.index)

    def add_edge(self, intersection, intersection2):
        label = str(intersection['latitude']) + "___" + str(intersection['longitude'])
        label2 = str(intersection2['latitude']) + "___" + str(intersection2['longitude'])

        self.edges.add((self.index[label], self.index[label2]))

    def get_point_by_label(self, label):
        pass

    def get_point(self, idx):
        return self.points[idx]

    def to_json(self):
        points = []
        for point in self.points:
            item = {
                'label': point.label(),
                'streets': list(point.streets)
            }
            points.append(item)
        return {"index": self.index, "edges": list(self.edges), "points": points}

    def from_json(self, dict_map):
        self.index = dict_map['index']
        self.edges = set(map(lambda x: tuple(x), dict_map['edges']))
        self.points = []
        for point in dict_map['points']:
            lat, lng = point['label'].split('___')
            streets = list(point['streets'])
            p = Point({
                "latitude": lat,
                "longitude": lng,
                "street_a": streets[0], "street_b": streets[1]
            })
            for _ in streets[2:]:
                p.add_street(streets[0])
                p.add_street(streets[1])
            self.points.append(p)

    def neighbours(self):
        neighbour_list = [set() for i in range(len(self.points))]
        for x, y in self.edges:
            if x != y:
                neighbour_list[x].add(y)
                neighbour_list[y].add(x)
        return neighbour_list

    def to_streets(self):
        streets = {}
        for idx, point in enumerate(self.points):
            for s in point.streets:
                if s in streets:
                    streets[s].append(idx)
                else:
                    streets[s] = [idx]
        streets = {x: streets[x] for x in streets if len(streets[x]) > 3}

        response = {}
        for street in streets:
            st = streets[street]
            w = self._sort(st[0], st[1:])
            response[street] = [ww[1] for ww in w]
        return response
