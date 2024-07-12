import re
import geojson
import dendropy
import numpy as np
import pandas as pd
from spatial_layer_generator.time_conversion import convert_datetext_to_datetime, convert_datetime_to_decimal_year, convert_decimal_year_to_datetime
from spatial_layer_generator.branch_processor import iterate_tree


def process_discrete_phylogeography(tree, mostRecentTip, date_format, location, location_list, extension):
    print("Started processing, please wait...")
    data_frame, feature_collection = handle_discrete_tree(tree, mostRecentTip, date_format, location, location_list)
    if extension == "csv":
        output = tree + '.output.csv'
        with open(output, 'w') as f:
            data_frame.to_csv(f, index=False)
    elif extension == "geojson":
        output = tree + '.output.geojson'
        with open(output, 'w') as f:
            geojson.dump(feature_collection, f)
    print('The result has been successfully stored as "' + output + '" in the current directory!')


def handle_discrete_tree(tree_path, most_recent_tip, date_format, location, location_list):
    tree = dendropy.Tree.get(path=tree_path, schema='nexus', preserve_underscores=True)
    delimiter = re.compile(r'[|\_]+')
    location_pattern = location[0] + '='
    match_quoted_string = re.compile(r'\"(.*)\"')
    not_root = False
    is_float = False
    branches = []
    contours = []
    id = 0

    try:
        most_recent_tip_time = float(most_recent_tip)
        is_float = True
    except ValueError:
        most_recent_tip_date = convert_datetext_to_datetime(most_recent_tip, date_format)
        most_recent_tip_time = convert_datetime_to_decimal_year(most_recent_tip_date)

    for edge in tree.preorder_edge_iter():
        id += 1
        branch = process_edge(edge, most_recent_tip_time, is_float, date_format, delimiter, id, location, location_pattern, match_quoted_string, location_list, not_root)
        branches.append(branch)
        not_root = True

    iterate_tree(branches)

    for branch in branches:
        branch = finalize_branch(branch, contours)
    
    data_frame = pd.DataFrame(branches)
    contour_collection = geojson.FeatureCollection(contours)
    return data_frame, contour_collection


def process_edge(edge, most_recent_tip_time, is_float, date_format, delimiter, id, location, location_pattern, match_quoted_string, location_list, not_root):
    child_node = edge.head_node
    branch_type = 'Internal'
    branch_length = edge.length if edge.length else 0.0
    ending_time = 0.0
    starting_time = 0.0

    if child_node.is_leaf():
        branch_type = 'External'
        ending_time, starting_time = process_leaf_node(child_node, most_recent_tip_time, is_float, date_format, branch_length, delimiter)
    
    branch = {
        'visited_times': 0,
        'id': id,
        'type': branch_type,
        'length': branch_length,
        'start_time': starting_time,
        'end_time': ending_time,
        'start_name': None,
        'start_lat': None,
        'start_lon': None,
        'end_name': None,
        'end_lat': None,
        'end_lon': None
    }

    parse_and_assign_location_info(branch, edge, location, location_pattern, match_quoted_string, location_list, not_root)
    
    return branch


def process_leaf_node(node, most_recent_tip_time, is_float, date_format, branch_length, delimiter):
    ending_time = 0.0
    starting_time = 0.0
    no_height = True
    
    for annotation in node.annotations:
        if annotation.name == 'height':
            no_height = False
            ending_time = most_recent_tip_time - float(annotation.value)
            starting_time = ending_time - branch_length
    
    if no_height:
        label = node.taxon.label
        name_elements = re.split(delimiter, label)
        time_element = name_elements[-1]
        if is_float:
            ending_time = float(time_element)
        else:
            ending_date = convert_datetext_to_datetime(time_element, date_format)
            ending_time = convert_datetime_to_decimal_year(ending_date)
        starting_time = ending_time - branch_length
    
    return ending_time, starting_time


def parse_and_assign_location_info(branch, edge, location, location_pattern, match_quoted_string, location_list, not_root):
    parent_node = edge.tail_node
    if not_root:
        starting_annotations = parent_node.annotations
        branch['start_name'], branch['start_lat'], branch['start_lon'] = parse_location_info(starting_annotations, location[0], location_pattern, match_quoted_string, location_list)
    ending_annotations = edge.head_node.annotations
    branch['end_name'], branch['end_lat'], branch['end_lon'] = parse_location_info(ending_annotations, location[0], location_pattern, match_quoted_string, location_list)


def parse_location_info(annotations, location_name, location_pattern, match_quoted_string, location_list):
    location_info = None
    
    for annotation in annotations:
        if annotation.name == location_name:
            location_info = annotation.value
            break

    if location_info is None:
        location_info = parse_locations_from_one_annotation(annotations, location_pattern, match_quoted_string)
    
    return fetch_coordinates_from_location_list(location_info, location_list)


def fetch_coordinates_from_location_list(location_info, location_list):
    df_list = pd.read_csv(location_list)
    
    if '+' in location_info:
        locations = location_info.split('+')
        location_info = np.random.choice(locations)
    
    matched_location_info = df_list.loc[df_list['location'] == location_info].iloc[0]
    location_info, latitude, longitude = matched_location_info['location'], matched_location_info['latitude'], matched_location_info['longitude']
    return location_info, latitude, longitude


def parse_locations_from_one_annotation(annotations, location_pattern, match_quoted_string):
    location_info = None
    for annotation in annotations:
        annotation_value = annotation.value
        if isinstance(annotation_value, str):
            annotation_value = [annotation_value]
        for value in annotation_value:
            if location_pattern in value:
                location_info = match_quoted_string.findall(value)[0]
    return location_info


def finalize_branch(branch, contours):
    del branch['visited_times']
    branch['start_time'] = convert_decimal_year_to_datetime(branch['start_time'])
    branch['end_time'] = convert_decimal_year_to_datetime(branch['end_time'])
    
    if branch['length'] == 0.0:
        branch['start_name'] = branch['end_name']
        branch['start_lat'] = branch['end_lat']
        branch['start_lon'] = branch['end_lon']
    
    contour = geojson.Feature(geometry=geojson.Polygon([]), properties=branch)
    contours.append(contour)
    
    return branch
