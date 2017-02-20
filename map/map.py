class Point(object):
    def __init__(self, intersection ):
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

    def add_point(self, intersection):
        label = str(intersection['latitude']) + "___" + str(intersection['longitude'])
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
        print(self.index)
        print("********************************************************************")
        print(self.edges)
        print("********************************************************************")
        print(points)

        return {"index": self.index, "edges": list(self.edges), "points": points}

    def from_json(self, dict_map):
        self.index = dict_map['index']
        self.edges = set(map(lambda x :tuple(x),dict_map['edges']))
        self.points = []
        for point in dict_map['points']:
            lat, lng = point['label'].split('___')
            streets = list(point['streets'])
            p = Point({"latitude":lat, "longitude":lng, "street_a":streets[0], "street_b":streets[1]})
            for _ in streets[2:]:
                p.add_street(streets[0])
                p.add_street(streets[1])
            self.points.append(p)

    def neighbours(self):
        neighbour_list = [set() for i in range(len(self.points))]
        for x,y in self.edges:
            if x!=y:
                neighbour_list[x].add(y)
                neighbour_list[y].add(x)
        return neighbour_list
