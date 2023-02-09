import baltic
import geojson
import pandas as pd
from spatial_layer_generator.time_conversion import *


def handle_continuous_tree(tree, location):
    loaded_tree = baltic.loadNexus(tree)
    tree_members = loaded_tree.traverse_tree(include_condition=lambda k: k)
    branches = []
    features = []
    counter = 0

    for member in tree_members:
        name = member.name if isinstance(member, baltic.leaf) else 'None'
        end_time = member.absoluteTime
        end_date = convert_decimal_year_to_datetime(end_time)
        start_time = member.parent.absoluteTime if counter != 0 else end_time
        start_date = convert_decimal_year_to_datetime(start_time)

        end_annotation = member.traits
        contour_1 = {}
        contour_2 = {}
        polygons = []
        for key in end_annotation.keys():
            if 'location1_80%HPD' in key:
                contour_1[key] = end_annotation[key]
            if 'location2_80%HPD' in key:
                contour_2[key] = end_annotation[key]
        if contour_2 and contour_1:
            for key_2 in contour_2.keys():
                for key_1 in contour_1.keys():
                    if key_2[-1] == key_1[-1]:
                        value_2 = contour_2.get(key_2)
                        coordinates_2 = [float(i) for i in value_2]
                        value_1 = contour_1.get(key_1)
                        coordinates_1 = [float(i) for i in value_1]
                        linear_ring = list(zip(coordinates_2, coordinates_1))
                        polygon = geojson.Polygon([linear_ring])
                        polygons.append(polygon)

        start_annotation = member.parent.traits
        end_latitude, end_longitude = 0.0, 0.0
        start_latitude, start_longitude = 0.0, 0.0
        if len(location) == 2:
            end_latitude = end_annotation.get(location[0])
            end_longitude = end_annotation.get(location[1])
            start_latitude = start_annotation.get(location[0]) if counter != 0 else end_latitude
            start_longitude = start_annotation.get(location[1]) if counter != 0 else end_longitude
        elif len(location) == 1:
            end_latitude = end_annotation.get(location[0])[0]
            end_longitude = end_annotation.get(location[0])[1]
            start_latitude = start_annotation.get(location[0])[0] if counter != 0 else end_latitude
            start_longitude = start_annotation.get(location[0])[1] if counter != 0 else end_longitude

        counter += 1
        branch = dict(id=counter, name=name, start_time=start_date, end_time=end_date, start_latitude=start_latitude,
                      start_longitude=start_longitude, end_latitude=end_latitude, end_longitude=end_longitude)
        branches.append(branch)

        if polygons:
            for polygon in polygons:
                feature = geojson.Feature(geometry=polygon, properties=branch)
                features.append(feature)
        else:
            feature = geojson.Feature(geometry=geojson.Polygon([]), properties=branch)
            features.append(feature)

    data_frame = pd.DataFrame(branches)
    feature_collection = geojson.FeatureCollection(features)
    return data_frame, feature_collection
