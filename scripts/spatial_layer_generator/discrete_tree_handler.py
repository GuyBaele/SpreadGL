import re
import geojson
import dendropy
import numpy as np
import pandas as pd
from spatial_layer_generator.time_conversion import *
from spatial_layer_generator.branch_processor import *


def handle_discrete_tree(tree, mostRecentTip, location, location_list):
    tree = dendropy.Tree.get(path=tree, schema='nexus', preserve_underscores=True)
    delimiter = re.compile(r'[|\_]+')
    no_height = True
    not_root = False
    branches = []
    contours = []
    id = 0

    if type(mostRecentTip) == str:
        mostRecentTipDate = convert_datetext_to_datetime(mostRecentTip)
        mostRecentTipTime = convert_datetime_to_decimal_year(mostRecentTipDate)
    elif type(mostRecentTip) == float:
        mostRecentTipTime = mostRecentTip

    for edge in tree.preorder_edge_iter():
        id += 1
        branch_type = 'Internal'
        branch_length = edge.length if edge.length else 0.0
        # Parse time
        ending_time = 0.0
        starting_time = 0.0
        child_node = edge.head_node
        if child_node.is_leaf():
            branch_type = 'External'
            for annotation in child_node.annotations:
                if annotation.name == 'height':
                    no_height = False
                    ending_time = mostRecentTipTime - float(annotation.value)
                    starting_time = ending_time - branch_length
            if no_height:
                label = child_node.taxon.label
                name_elements = re.split(delimiter, label)
                ending_date = convert_datetext_to_datetime(name_elements[-1])
                ending_time = convert_datetime_to_decimal_year(ending_date)
                starting_time = ending_time - branch_length
        branch = dict(visited_times=0, id=id, type=branch_type, branch_length=branch_length, starting_time=starting_time, ending_time=ending_time)
        # Parse location
        parent_node = edge.tail_node
        if not_root:
            starting_annotation = parent_node.annotations
            for annotation in starting_annotation:
                if annotation.name == location[0]:
                    branch['starting_'+location[0]+'_name'], branch['starting_'+location[0]+'_latitude'], branch['starting_'+location[0]+'_longitude'] = fetch_coordinates_from_location_list(annotation.value, location_list)
        ending_annotation = child_node.annotations
        for annotation in ending_annotation:
            if annotation.name == location[0]:
                branch['ending_'+location[0]+'_name'], branch['ending_'+location[0]+'_latitude'], branch['ending_'+location[0]+'_longitude'] = fetch_coordinates_from_location_list(annotation.value, location_list)
        branches.append(branch)
        not_root = True

    iterate_tree(branches)

    for branch in branches:
        del branch['visited_times']
        branch['starting_time'] = convert_decimal_year_to_datetime(branch['starting_time'])
        branch['ending_time'] = convert_decimal_year_to_datetime(branch['ending_time'])
        if branch['branch_length'] == 0.0:
            branch['starting_'+location[0]+'_name'] = branch['ending_'+location[0]+'_name']
            branch['starting_'+location[0]+'_latitude'] = branch['ending_'+location[0]+'_latitude']
            branch['starting_'+location[0]+'_longitude'] = branch['ending_'+location[0]+'_longitude']
        contour = geojson.Feature(geometry=geojson.Polygon([]),properties=branch)
        contours.append(contour)

    data_frame = pd.DataFrame(branches)
    contour_collection = geojson.FeatureCollection(contours)
    return data_frame, contour_collection


def fetch_coordinates_from_location_list(location_info, location_list):
    df_list = pd.read_csv(location_list)
    # Pick up a random location just in case
    if '+' in location_info:
        locations = location_info.split('+')
        location_info = np.random.choice(locations)
    matched_location_info = np.asarray(df_list.loc[df_list['location'] == location_info].values)[0]
    location_info, latitude, longitude = matched_location_info[0], matched_location_info[1], matched_location_info[2]
    return location_info, latitude, longitude
