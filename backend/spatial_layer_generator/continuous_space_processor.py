import re
import geojson
import dendropy
import pandas as pd
from spatial_layer_generator.time_conversion import convert_datetext_to_datetime, convert_datetime_to_decimal_year, convert_decimal_year_to_datetime

def extract_hpd_percentage(name):
    m = re.search(r'(\d+)%\s*HPD|(\d+)[\s_-]*HPD|HPD[\s_-]*(\d+)', name, re.IGNORECASE)
    if m:
        for g in m.groups():
            if g is not None:
                return g
    return "80"  # Default fallback


def process_continuous_phylogeography(tree, mostRecentTip, date_format, location, extension, return_data=False):
    print("Started processing continuous phylogeography, please wait...")
    
    if return_data:
        return handle_continuous_tree(tree, mostRecentTip, date_format, location, extension, return_data=True)
        
    data_frame, feature_collection = handle_continuous_tree(tree, mostRecentTip, date_format, location, extension, return_data=False)

    if extension == "csv":
        output = tree + '.output.csv'
        with open(output, 'w') as f:
            data_frame.to_csv(f, index=False)
        print('The CSV result has been successfully stored as "' + output + '" in the current directory!')
        
    elif extension == "geojson":
        output = tree + '.output.geojson'
        with open(output, 'w') as f:
            geojson.dump(feature_collection, f)
        print('The comprehensive GeoJSON result has been successfully stored as "' + output + '" in the current directory!')


def handle_continuous_tree(tree_path, most_recent_tip, date_format, location, extension, return_data=False):
    tree = dendropy.Tree.get(path=tree_path, schema='nexus', preserve_underscores=True)
    delimiter = re.compile(r'[|\_]+')
    match_coordinate = re.compile(r'-?\d+\.?\d+')
    not_root = False
    is_float = False
    branches = []
    trip_features = []
    hpd_features = []
    id = 0

    try:
        most_recent_tip_time = float(most_recent_tip)
        is_float = True
    except ValueError:
        most_recent_tip_date = convert_datetext_to_datetime(most_recent_tip, date_format)
        most_recent_tip_time = convert_datetime_to_decimal_year(most_recent_tip_date)

    # TEMPORAL IMPUTATION
    for node in tree.postorder_node_iter():
        if node.is_leaf():
            node.absolute_time = process_leaf_node(node, most_recent_tip_time, is_float, date_format, delimiter)
        else:
            child = node.child_nodes()[0]
            raw_length = child.edge.length if child.edge.length is not None else 0.0
            node.absolute_time = child.absolute_time - float(raw_length)

    # EDGE EXTRACTION
    for edge in tree.preorder_edge_iter():
        id += 1
        branch = process_edge(edge, id)
        branch = process_location_info(edge, branch, location, match_coordinate, not_root)
        branches.append(branch)
        not_root = True

    finalized_branches = []
    for branch in branches:
        fb = finalize_branch_geometries_split(branch, trip_features, hpd_features, extension if not return_data else "geojson")
        finalized_branches.append(fb)

    if return_data:
        return {
            "branches": finalized_branches,
            "trip_geojson": geojson.FeatureCollection(trip_features),
            "hpd_geojson": geojson.FeatureCollection(hpd_features)
        }

    if extension == "csv":
        data_frame = pd.DataFrame(finalized_branches)
        return data_frame, None
    elif extension == "geojson":
        # Combine line and polygon features for the old format
        all_features = trip_features + hpd_features
        feature_collection = geojson.FeatureCollection(all_features)
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


def process_edge(edge, id):
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

    return {
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


def process_location_info(edge, branch, location, match_coordinate, not_root):
    parent_node = edge.tail_node
    if not_root:
        starting_annotation = parent_node.annotations
        for annotation in starting_annotation:
            if len(location) == 1 and annotation.name == location[0]:
                try:
                    branch['start_lat'] = float(annotation.value[0])
                    branch['start_lon'] = float(annotation.value[1])
                except (ValueError, TypeError, IndexError):
                    pass
            elif len(location) == 2:
                if annotation.name == location[0]:
                    try: branch['start_lat'] = float(annotation.value)
                    except (ValueError, TypeError): pass
                if annotation.name == location[1]:
                    try: branch['start_lon'] = float(annotation.value)        
                    except (ValueError, TypeError): pass
        if not branch['start_lat'] or not branch['start_lon']:
            if len(location) == 1:
                branch['start_lat'], branch['start_lon'] = parse_coordinates_from_one_annotation(starting_annotation, location, match_coordinate)
            elif len(location) == 2:
                branch['start_lat'], branch['start_lon'] = parse_coordinates_from_two_annotations(starting_annotation, location, match_coordinate)
    
    child_node = edge.head_node
    ending_annotation = child_node.annotations
    contour_1, contour_2 = {}, {}
    single_polygons = []
    for annotation in ending_annotation:
        if len(location) == 1:
            if annotation.name == location[0]:
                try:
                    branch['end_lat'] = float(annotation.value[0])
                    branch['end_lon'] = float(annotation.value[1])
                except (ValueError, TypeError, IndexError):
                    pass
            elif location[0] in annotation.name and 'HPD' in annotation.name:
                try:
                    linear_ring = []
                    # Check if it is a list/tuple
                    if isinstance(annotation.value, (list, tuple)):
                        if len(annotation.value) > 0:
                            first_elem = annotation.value[0]
                            # If it's a flat list of numbers
                            if isinstance(first_elem, (int, float)) or (isinstance(first_elem, str) and not ',' in first_elem and not '[' in first_elem):
                                coords_floats = []
                                for val in annotation.value:
                                    try: coords_floats.append(float(val))
                                    except Exception: pass
                                if len(coords_floats) >= 2:
                                    linear_ring = [[coords_floats[i+1], coords_floats[i]] for i in range(0, len(coords_floats) - 1, 2)]
                            else:
                                # It's a list of pairs/lists or strings
                                for coord in annotation.value:
                                    if isinstance(coord, (list, tuple)) and len(coord) >= 2:
                                        linear_ring.append([float(coord[1]), float(coord[0])])
                                    elif isinstance(coord, str):
                                        coords = match_coordinate.findall(coord)
                                        if len(coords) >= 2:
                                            linear_ring.append([float(coords[1]), float(coords[0])])
                    elif isinstance(annotation.value, str):
                        # If it's a single string with all coordinates
                        coords = match_coordinate.findall(annotation.value)
                        if len(coords) >= 2:
                            coords_floats = [float(x) for x in coords]
                            linear_ring = [[coords_floats[i+1], coords_floats[i]] for i in range(0, len(coords_floats) - 1, 2)]
                            
                    if linear_ring:
                        polygon = geojson.Polygon([linear_ring])
                        pct = extract_hpd_percentage(annotation.name)
                        single_polygons.append({
                            "geometry": polygon,
                            "hpd_level": pct
                        })
                except Exception:
                    pass
        elif len(location) == 2:
            if annotation.name == location[0]:
                try: branch['end_lat'] = float(annotation.value)
                except (ValueError, TypeError): pass
            if annotation.name == location[1]:
                try: branch['end_lon'] = float(annotation.value)
                except (ValueError, TypeError): pass
            if location[0] in annotation.name and 'HPD' in annotation.name:
                contour_1[annotation.name] = annotation.value
            if location[1] in annotation.name and 'HPD' in annotation.name:
                contour_2[annotation.name] = annotation.value
    if not branch['end_lat'] or not branch['end_lon']:
        if len(location) == 1:
            branch['end_lat'], branch['end_lon'] = parse_coordinates_from_one_annotation(ending_annotation, location, match_coordinate)
        elif len(location) == 2:
            branch['end_lat'], branch['end_lon'] = parse_coordinates_from_two_annotations(ending_annotation, location, match_coordinate)
    
    if len(location) == 1:
        branch['contours'] = single_polygons
    else:
        branch = process_contours(branch, contour_1, contour_2)
    return branch


def process_contours(branch, contour_1, contour_2):
    polygons = []
    if contour_2 and contour_1:
        for key_2 in contour_2.keys():
            for key_1 in contour_1.keys():
                pct_2 = extract_hpd_percentage(key_2)
                pct_1 = extract_hpd_percentage(key_1)
                idx_2 = key_2.split('_')[-1]
                idx_1 = key_1.split('_')[-1]
                if pct_2 == pct_1 and idx_2 == idx_1:
                    try:
                        coordinates_2 = [float(i) for i in contour_2.get(key_2)]
                        coordinates_1 = [float(i) for i in contour_1.get(key_1)]
                        linear_ring = list(zip(coordinates_2, coordinates_1))
                        polygon = geojson.Polygon([linear_ring])
                        polygons.append({
                            "geometry": polygon,
                            "hpd_level": pct_2
                        })
                    except (ValueError, TypeError):
                        pass
    branch['contours'] = polygons
    return branch


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
                try:
                    coords = match_coordinate.findall(value)
                    parsed_latitude = float(coords[0])
                    parsed_longitude = float(coords[1])
                except (ValueError, TypeError, IndexError):
                    pass
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
                try: parsed_latitude = float(match_coordinate.findall(value)[0])
                except (ValueError, TypeError, IndexError): pass
            if location_pattern_2 in value:
                try: parsed_longitude = float(match_coordinate.findall(value)[0])
                except (ValueError, TypeError, IndexError): pass
    return parsed_latitude, parsed_longitude


def finalize_branch_geometries_split(branch, trip_features, hpd_features, extension):
    # Store numeric representations of decimal times if needed for calculations,
    # but they will not be returned in the final JSON objects.
    start_time_numeric = float(branch['start_time'])
    end_time_numeric = float(branch['end_time'])

    branch['start_time'] = convert_decimal_year_to_datetime(branch['start_time'])
    branch['end_time'] = convert_decimal_year_to_datetime(branch['end_time'])
    
    if branch['length'] == 0.0:
        branch['start_lat'] = branch['end_lat']
        branch['start_lon'] = branch['end_lon']       

    if extension == "geojson":
        # Prepare valid metadata properties by isolating the geometry objects
        branch_properties = {k: v for k, v in branch.items() if k != 'contours'}
        branch_properties.pop('start_time_numeric', None)
        branch_properties.pop('end_time_numeric', None)
        branch_properties.pop('hpd_level', None)

        # Construct the LineString (Trip Vector)
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
            
            line_feature = geojson.Feature(
                geometry=geojson.LineString(line_coordinates), 
                properties=branch_properties
            )
            trip_features.append(line_feature)

            # Construct the Polygons (HPD Contours)
            if branch['contours']:
                for contour_item in branch['contours']:
                    polygon_properties = branch_properties.copy()
                    try:
                        polygon_properties['hpd_level'] = int(contour_item.get('hpd_level', '80'))
                    except (ValueError, TypeError):
                        polygon_properties['hpd_level'] = contour_item.get('hpd_level', '80')
                    
                    polygon_feature = geojson.Feature(
                        geometry=contour_item['geometry'], 
                        properties=polygon_properties
                    )
                    hpd_features.append(polygon_feature)
        except (ValueError, TypeError, KeyError):
            pass

    branch.pop('start_time_numeric', None)
    branch.pop('end_time_numeric', None)
    branch.pop('hpd_level', None)
    del branch['contours']
    return branch