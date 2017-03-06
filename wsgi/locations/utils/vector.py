import math


def vector_length(vector):
    return math.sqrt(vector[0]**2 + vector[1]**2)


def dot(a, b):
    la = vector_length(a)
    lb = vector_length(b)

    if la*lb == 0:
        return 0
    return (a[0]*b[0] + a[1]*b[1]) / (la * lb)

