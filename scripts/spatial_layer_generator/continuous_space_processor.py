import re
import geojson
import dendropy
import pandas as pd
from spatial_layer_generator.time_conversion import convert_datetext_to_datetime, convert_datetime_to_decimal_year, convert_decimal_year_to_datetime
from spatial_layer_generator.branch_processor import iterate_tree

def process_continuous_phylogeography(tree, mostRecentTip, date_format, location, extension):
    print("Started processing, please wait...")
    data_frame, feature_collection = handle_continuous_tree(tree, mostRecentTip, date_format, location)
    if extension == "csv":
        output = tree + '.output.csv'
        with open(output, 'w') as f:
            data_frame.to_csv(f, index=False)
    elif extension == "geojson":
        output = tree + '.output.geojson'
        with open(output, 'w') as f:
            geojson.dump(feature_collection, f)
    print('The result has been successfully stored as "' + output + '" in the current directory!')


def handle_continuous_tree(tree_path, most_recent_tip, date_format, location):
    tree = dendropy.Tree.get(path=tree_path, schema='nexus', preserve_underscores=True)
    delimiter = re.compile(r'[|\_]+')
    match_coordinate = re.compile(r'-?\d+\.?\d+')
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
        branch = process_edge(edge, most_recent_tip_time, is_float, date_format, delimiter, id)
        branch = process_location_info(edge, branch, location, match_coordinate, not_root)
        branches.append(branch)
        not_root = True

    iterate_tree(branches)

    contours = finalize_contours(branches, contours)
    data_frame = pd.DataFrame(branches)
    contour_collection = geojson.FeatureCollection(contours)
    return data_frame, contour_collection


def process_edge(edge, most_recent_tip_time, is_float, date_format, delimiter, id):
    branch_length = edge.length if edge.length else 0.0
    ending_time, starting_time, branch_type = get_edge_times(edge, most_recent_tip_time, is_float, date_format, branch_length, delimiter)

    return {
        'visited_times': 0,
        'id': id,
        'type': branch_type,
        'length': branch_length,
        'start_time': starting_time,
        'end_time': ending_time,
        'start_lat': None,
        'start_lon': None,
        'end_lat': None,
        'end_lon': None,
        'contours': []
    }


def get_edge_times(edge, most_recent_tip_time, is_float, date_format, branch_length, delimiter):
    child_node = edge.head_node
    ending_time = 0.0
    starting_time = 0.0
    branch_type = 'Internal'

    if child_node.is_leaf():
        ending_time, starting_time = get_leaf_times(child_node, most_recent_tip_time, is_float, date_format, branch_length, delimiter)
        branch_type = 'External'
        
    return ending_time, starting_time, branch_type


def get_leaf_times(node, most_recent_tip_time, is_float, date_format, branch_length, delimiter):
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


def process_location_info(edge, branch, location, match_coordinate, not_root):
    parent_node = edge.tail_node
    if not_root:
        starting_annotation = parent_node.annotations
        for annotation in starting_annotation:
            if len(location) == 1 and annotation.name == location[0]:
                branch['start_lat'] = float(annotation.value[0])
                branch['start_lon'] = float(annotation.value[1])
            elif len(location) == 2:
                if annotation.name == location[0]:
                    branch['start_lat'] = float(annotation.value)
                if annotation.name == location[1]:
                    branch['start_lon'] = float(annotation.value)        
        if not branch['start_lat'] or not branch['start_lon']:
            if len(location) == 1:
                branch['start_lat'], branch['start_lon'] = parse_coordinates_from_one_annotation(starting_annotation, location, match_coordinate)
            elif len(location) == 2:
                branch['start_lat'], branch['start_lon'] = parse_coordinates_from_two_annotations(starting_annotation, location, match_coordinate)
    
    child_node = edge.head_node
    ending_annotation = child_node.annotations
    contour_1, contour_2 = {}, {}
    for annotation in ending_annotation:
        if len(location) == 1 and annotation.name == location[0]:
            branch['end_lat'] = float(annotation.value[0])
            branch['end_lon'] = float(annotation.value[1])
        elif len(location) == 2:
            if annotation.name == location[0]:
                branch['end_lat'] = float(annotation.value)
            if annotation.name == location[1]:
                branch['end_lon'] = float(annotation.value)
            if location[0] in annotation.name and 'HPD' in annotation.name:
                contour_1[annotation.name] = annotation.value
            if location[1] in annotation.name and 'HPD' in annotation.name:
                contour_2[annotation.name] = annotation.value
    if not branch['end_lat'] or not branch['end_lon']:
        if len(location) == 1:
            branch['end_lat'], branch['end_lon'] = parse_coordinates_from_one_annotation(ending_annotation, location, match_coordinate)
        elif len(location) == 2:
            branch['end_lat'], branch['end_lon'] = parse_coordinates_from_two_annotations(ending_annotation, location, match_coordinate)
    
    branch = process_contours(branch, contour_1, contour_2)
    return branch


def process_contours(branch, contour_1, contour_2):
    polygons = []
    if contour_2 and contour_1:
        for key_2 in contour_2.keys():
            for key_1 in contour_1.keys():
                if key_2[-1] == key_1[-1]:
                    coordinates_2 = [float(i) for i in contour_2.get(key_2)]
                    coordinates_1 = [float(i) for i in contour_1.get(key_1)]
                    linear_ring = list(zip(coordinates_2, coordinates_1))
                    polygon = geojson.Polygon([linear_ring])
                    polygons.append(polygon)
    branch['contours'] = polygons
    return branch


def finalize_contours(branches, contours):
    for branch in branches:
        del branch['visited_times']
        branch['start_time'] = convert_decimal_year_to_datetime(branch['start_time'])
        branch['end_time'] = convert_decimal_year_to_datetime(branch['end_time'])
        if branch['length'] == 0.0:
            branch['start_lat'] = branch['end_lat']
            branch['start_lon'] = branch['end_lon']       
        if branch['contours']:
            for polygon in branch['contours']:
                contour = geojson.Feature(geometry=polygon, properties={k: v for k, v in branch.items() if k != 'contours'})
                contours.append(contour)
        else:
            contour = geojson.Feature(geometry=geojson.Polygon([]), properties={k: v for k, v in branch.items() if k != 'contours'})
            contours.append(contour)
        del branch['contours']
    return contours


def parse_coordinates_from_one_annotation(annotations, location, match_coordinate):
    parsed_latitude = None
    parsed_longitude = None
    location_pattern = location[0] + '='
    for annotation in annotations:
        annotation_value = annotation.value
        if isinstance(annotation_value, str):
            annotation_value = [annotation_value]
        for value in annotation_value:
            if location_pattern in value:
                parsed_latitude = float(match_coordinate.findall(value)[0])
                parsed_longitude = float(match_coordinate.findall(value)[1])
    return parsed_latitude, parsed_longitude


def parse_coordinates_from_two_annotations(annotations, location, match_coordinate):
    parsed_latitude = None
    parsed_longitude = None
    location_pattern_1 = location[0] + '='
    location_pattern_2 = location[1] + '='    
    for annotation in annotations:
        annotation_value = annotation.value
        if isinstance(annotation_value, str):
            annotation_value = [annotation_value]
        for value in annotation_value:
            if location_pattern_1 in value:
                parsed_latitude = float(match_coordinate.findall(value)[0])
            if location_pattern_2 in value:
                parsed_longitude = float(match_coordinate.findall(value)[0])
    return parsed_latitude, parsed_longitude
