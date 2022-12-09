import random
import json
import shapely.geometry


def match_location(location):
    path = '/Users/u0150975/Downloads/Visualisation/Discrete Space Examples/EuropeMap.json'
    data = json.load(open(path))
    for feature in data['features']:
        if feature['properties']["NAME"] == location:
            if feature['geometry']['type'] == "MultiPolygon":
                linear_rings = feature['geometry']['coordinates']
                probability = []
                for i in range(len(linear_rings)):
                    probability.append(len(linear_rings[i][0]))
                selected_ring = random.choices(linear_rings, weights=probability)[0][0]
            elif feature['geometry']['type'] == "Polygon":
                selected_ring = feature['geometry']['coordinates'][0]
            print(len(selected_ring))
            polygon = shapely.geometry.Polygon(selected_ring)
            return generate_random(polygon)


def generate_random(polygon):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    while len(points) < 1:
        pnt = shapely.geometry.Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(pnt):
            points.append(pnt.coords[:])
    return points[0][0]
