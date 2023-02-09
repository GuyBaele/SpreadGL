import baltic
import geojson
import pandas as pd
import numpy as np
from spatial_layer_generator.time_conversion import *


def handle_discrete_tree(tree, location, location_list):
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
        end_location = end_annotation.get(location[0])
        end_location, end_latitude, end_longitude = fetch_coordinates_from_location_list(end_location, location_list)
        start_annotation = member.parent.traits
        start_location = start_annotation.get(location[0]) if counter != 0 else end_location
        start_location, start_latitude, start_longitude = fetch_coordinates_from_location_list(start_location, location_list)

        counter += 1
        branch = dict(id=counter, name=name, start_time=start_date, end_time=end_date,
                      start_location=start_location, start_latitude=start_latitude, start_longitude=start_longitude,
                      end_location=end_location, end_latitude=end_latitude, end_longitude=end_longitude)
        branches.append(branch)
        feature = geojson.Feature(geometry=geojson.Polygon([]), properties=branch)
        features.append(feature)

    data_frame = pd.DataFrame(branches)
    feature_collection = geojson.FeatureCollection(features)
    return data_frame, feature_collection


def fetch_coordinates_from_location_list(location_info, location_list):
    df_list = pd.read_csv(location_list)
    # Pick up a random location just in case
    if '+' in location_info:
        locations = location_info.split('+')
        location_info = np.random.choice(locations)
    matched_location_info = np.asarray(df_list.loc[df_list['location'] == location_info].values)[0]
    location_info, latitude, longitude = matched_location_info[0], matched_location_info[1], matched_location_info[2]
    return location_info, latitude, longitude
