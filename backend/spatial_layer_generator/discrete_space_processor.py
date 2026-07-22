import re
import geojson
import dendropy
import numpy as np
import pandas as pd
from collections import Counter
from spatial_layer_generator.time_conversion import convert_datetext_to_datetime, convert_datetime_to_decimal_year, convert_decimal_year_to_datetime

def process_discrete_phylogeography(tree, mostRecentTip, date_format, location, location_list, extension, return_data=False):
    print("Started processing, please wait...")
    
    if return_data:
        return handle_discrete_tree(tree, mostRecentTip, date_format, location, location_list, extension, return_data=True)
        
    data_frame, feature_collection = handle_discrete_tree(tree, mostRecentTip, date_format, location, location_list, extension, return_data=False)

    if extension == "csv":
        output = tree + '.output.csv'
        with open(output, 'w') as f:
            data_frame.to_csv(f, index=False)
        print('The CSV result has been successfully stored as "' + output + '" in the current directory!')
        
    elif extension == "geojson":
        output = tree + '.output.geojson'
        with open(output, 'w') as f:
            geojson.dump(feature_collection, f)
        print('The GeoJSON result has been successfully stored as "' + output + '" in the current directory!')


def handle_discrete_tree(tree_path, most_recent_tip, date_format, location, location_list, extension, return_data=False):
    tree = dendropy.Tree.get(path=tree_path, schema='nexus', preserve_underscores=True)
    coordinate_df = pd.read_csv(location_list)
    delimiter = re.compile(r'[|\_]+')
    location_pattern = location[0] + '='
    match_quoted_string = re.compile(r'\"(.*)\"')
    is_float = False
    branches = []
    features = []
    id = 0

    try:
        most_recent_tip_time = float(most_recent_tip)
        is_float = True
    except ValueError:
        most_recent_tip_date = convert_datetext_to_datetime(most_recent_tip, date_format)
        most_recent_tip_time = convert_datetime_to_decimal_year(most_recent_tip_date)

    # Two-Pass Topological Smoothing
    node_locations = {}
    
    def extract_loc(node):
        for ann in node.annotations:
            if ann.name == location[0]:
                return ann.value
        for ann in node.annotations:
            val = ann.value
            if isinstance(val, str): val = [val]
            for v in val:
                if location_pattern in str(v):
                    matches = match_quoted_string.findall(str(v))
                    if matches: return matches[0]
        return None

    for node in tree.postorder_node_iter():
        loc = extract_loc(node)
        if loc is not None:
            node_locations[node] = loc
        else:
            child_locs = [node_locations.get(c) for c in node.child_node_iter() if node_locations.get(c) is not None]
            if child_locs:
                node_locations[node] = Counter(child_locs).most_common(1)[0][0]
            else:
                node_locations[node] = None

    for node in tree.preorder_node_iter():
        if node_locations.get(node) is None:
            parent = node.parent_node
            if parent and node_locations.get(parent) is not None:
                node_locations[node] = node_locations[parent]
            else:
                node_locations[node] = "Unknown"

    unique_tree_locations = set()
    for loc in node_locations.values():
        if loc and loc != "Unknown":
            if isinstance(loc, str) and '+' in loc:
                for sub_loc in loc.split('+'):
                    unique_tree_locations.add(sub_loc.strip())
            else:
                unique_tree_locations.add(str(loc).strip())

    csv_locations = set(coordinate_df['location'].astype(str).str.strip().tolist())
    mismatched = unique_tree_locations - csv_locations
    if mismatched:
        raise ValueError(f"Location Mismatch: The following locations in the tree are not present in locations.csv: {', '.join(sorted(list(mismatched)))}")

    # TEMPORAL IMPUTATION
    for node in tree.postorder_node_iter():
        # 1. Prioritize reading the native timestamps of BEAST (applicable to all nodes, absolutely accurate)
        node_height = None
        for annotation in node.annotations:
            if annotation.name in ['height', 'height_median', 'height_mean']:
                node_height = float(annotation.value)
                break
                
        if node_height is not None:
            # Height represents the time backtracking from the latest sampling point (MRSD)
            node.absolute_time = most_recent_tip_time - node_height
            
        elif node.is_leaf():
            # 2. If a leaf node does not have a height tag, fall back to the time parsed from name.
            node.absolute_time = process_leaf_node(node, most_recent_tip_time, is_float, date_format, delimiter)
            
        else:
            # 3. Ultimate fallback solution: Estimate time based on branch lengths only for internal nodes that have no height tag at all.
            child = node.child_nodes()[0]
            raw_length = child.edge.length if child.edge.length is not None else 0.0
            node.absolute_time = child.absolute_time - float(raw_length)

    # EDGE EXTRACTION
    for edge in tree.preorder_edge_iter():
        id += 1
        branch = process_edge(edge, id, node_locations, coordinate_df)
        branches.append(branch)

    finalized_branches = []
    for branch in branches:
        fb = finalize_branch(branch, features, extension if not return_data else "geojson")
        finalized_branches.append(fb)
    
    if return_data:
        return {
            "branches": finalized_branches,
            "trip_geojson": geojson.FeatureCollection(features),
            "coordinate_df": coordinate_df
        }

    if extension == "csv":
        data_frame = pd.DataFrame(finalized_branches)
        return data_frame, None
    elif extension == "geojson":
        feature_collection = geojson.FeatureCollection(features)
        return None, feature_collection


def process_leaf_node(node, most_recent_tip_time, is_float, date_format, delimiter):
    for annotation in node.annotations:
        if annotation.name == 'height':
            return most_recent_tip_time - float(annotation.value)
    
    label = node.taxon.label
    name_elements = re.split(delimiter, label)
    time_element = name_elements[-1]
    
    if is_float:
        return float(time_element)
    else:
        ending_date = convert_datetext_to_datetime(time_element, date_format)
        return convert_datetime_to_decimal_year(ending_date)


def process_edge(edge, id, node_locations, coordinate_df):
    child_node = edge.head_node
    parent_node = edge.tail_node
    branch_type = 'External' if child_node.is_leaf() else 'Internal'
    
    raw_length = edge.length if edge.length is not None else 0.0
    branch_length = max(0.0, float(raw_length))
    
    ending_time = child_node.absolute_time
    if parent_node is not None:
        starting_time = parent_node.absolute_time
    else:
        starting_time = ending_time - branch_length

    if starting_time > ending_time:
        starting_time = ending_time
    
    branch = {
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

    parse_and_assign_location_info(branch, edge, node_locations, coordinate_df)
    return branch


def parse_and_assign_location_info(branch, edge, node_locations, coordinate_df):
    parent_node = edge.tail_node
    child_node = edge.head_node
    
    start_loc_name = node_locations.get(parent_node, "Unknown") if parent_node else "Unknown"
    end_loc_name = node_locations.get(child_node, "Unknown") if child_node else "Unknown"
    
    branch['start_name'], branch['start_lat'], branch['start_lon'] = fetch_coordinates_from_coordinate_df(start_loc_name, coordinate_df)
    branch['end_name'], branch['end_lat'], branch['end_lon'] = fetch_coordinates_from_coordinate_df(end_loc_name, coordinate_df)


def fetch_coordinates_from_coordinate_df(location_info, coordinate_df):
    if location_info and location_info != "Unknown":
        if '+' in location_info:
            locations = location_info.split('+')
            location_info = np.random.choice(locations)
            
        matched_location_info = coordinate_df.loc[coordinate_df['location'] == location_info]
        
        if not matched_location_info.empty:
            row = matched_location_info.iloc[0]
            return row['location'], row['latitude'], row['longitude']

    return "Unknown", "0.0", "0.0"


def finalize_branch(branch, features, extension):

    branch['start_time'] = convert_decimal_year_to_datetime(branch['start_time'])
    branch['end_time'] = convert_decimal_year_to_datetime(branch['end_time'])
    
    if branch['length'] == 0.0:
        branch['start_name'] = branch['end_name']
        branch['start_lat'] = branch['end_lat']
        branch['start_lon'] = branch['end_lon']

    # Conditionally construct the geographic LineString strictly for GeoJSON
    if extension == "geojson":
        try:
            start_lon = float(branch['start_lon'])
            start_lat = float(branch['start_lat'])
            end_lon = float(branch['end_lon'])
            end_lat = float(branch['end_lat'])
            
            start_ts = pd.to_datetime(branch['start_time']).timestamp()
            end_ts = pd.to_datetime(branch['end_time']).timestamp()
            
            mid_lon = (start_lon + end_lon) / 2
            mid_lat = (start_lat + end_lat) / 2
            mid_ts = (start_ts + end_ts) / 2
            
            line_coordinates = [
                [start_lon, start_lat, 0, int(start_ts)],
                [mid_lon, mid_lat, 0, int(mid_ts)],
                [end_lon, end_lat, 0, int(end_ts)]
            ]

            # Integrate metadata directly into the LineString properties
            combined_feature = geojson.Feature(
                geometry=geojson.LineString(line_coordinates), 
                properties=branch
            )
            features.append(combined_feature)
        except (ValueError, TypeError, KeyError):
            pass

    return branch