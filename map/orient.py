import math


def vector_length(vector):
    return math.sqrt(vector[0]**2 + vector[1]**2)


def dot(a, b):
    la = vector_length(a)
    lb = vector_length(b)

    if la*lb == 0:
        return 0
    return (a[0]*b[0] + a[1]*b[1]) / (la * lb)


def sort(m, idx_point, idx_points):
    point = m.points[idx_point]
    points = [m.points[idx] for idx in idx_points]

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


def sort_2(m, idx_point, idx_points, bonus):
    point = m.points[idx_point]
    points = [m.points[idx] for idx in idx_points] + bonus

    group = [(0.0, idx_point)]
    ry = float(points[0].latitude) - float(point.latitude)
    rx = float(points[0].longitude) - float(point.longitude)
    b_points = list(range(-1, -len(bonus) - 1, -1))
    # print(bonus,b_points)
    # print(zip(idx_points+b_points, points))
    # print(len(list(zip(idx_points + b_points, points))))
    for idx, i in zip(idx_points+b_points, points):
        dy = float(i.latitude) - float(point.latitude)
        dx = float(i.longitude) - float(point.longitude)
        alpha = 1
        if dot([rx, ry], [dx, dy]) < 0:
            alpha = -1
        re = vector_length([dx, dy]) * alpha
        group.append((re, idx))
    group.sort()
    return group
