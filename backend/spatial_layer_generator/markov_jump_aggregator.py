import geojson
import pandas as pd
from collections import Counter

def aggregate_markov_jumps(branches, coordinate_df, bayes_filter=None, bf_threshold=3.0):
    """
    Groups discrete branches by (start_name, end_name), counts the number of jumps,
    applies an optional Bayes Factor filter, and returns a GeoJSON FeatureCollection
    suitable for Kepler.gl ArcLayer.
    
    Args:
        branches (list): List of branch dicts from discrete_space_processor.
        coordinate_df (pd.DataFrame): DataFrame containing location coordinates.
        bayes_filter (pd.DataFrame or dict, optional): Dataframe or dict with Bayes factors for (start_name, end_name).
        bf_threshold (float): Threshold to filter out insignificant rates.
        
    Returns:
        geojson.FeatureCollection: Feature collection of arcs.
    """
    # 1. Build coordinate lookup dictionary
    coords_dict = {}
    for _, row in coordinate_df.iterrows():
        coords_dict[str(row['location']).strip()] = (float(row['longitude']), float(row['latitude']))

    # 2. Count transitions between different locations (excluding Unknown and self-loops)
    transition_tuples = []
    for b in branches:
        start = str(b.get('start_name')).strip()
        end = str(b.get('end_name')).strip()
        if start and end and start != "Unknown" and end != "Unknown" and start != end:
            transition_tuples.append((start, end))
            
    counts = Counter(transition_tuples)
    
    # 3. Process Bayes factor filtering if available
    bf_lookup = {}
    if bayes_filter is not None:
        # If it's a DataFrame, convert to dictionary
        if isinstance(bayes_filter, pd.DataFrame):
            for _, row in bayes_filter.iterrows():
                s = str(row['start_name']).strip()
                e = str(row['end_name']).strip()
                bf_lookup[(s, e)] = float(row['bayes_factor'])
        elif isinstance(bayes_filter, dict):
            bf_lookup = { (str(k[0]).strip(), str(k[1]).strip()): float(v) for k, v in bayes_filter.items() }

    features = []
    for (start, end), count in counts.items():
        # Check if locations are in coordinate dict
        if start not in coords_dict or end not in coords_dict:
            continue
            
        start_lon, start_lat = coords_dict[start]
        end_lon, end_lat = coords_dict[end]
        
        # Tabular properties mapping explicitly for Kepler.gl Arc Layer point-to-point column mapping
        properties = {
            'start_name': start,
            'end_name': end,
            'jump_weight': count,
            'start_lon': start_lon,
            'start_lat': start_lat,
            'end_lon': end_lon,
            'end_lat': end_lat
        }
        
        # Check Bayes Factor filter if provided
        bf_val = None
        if bayes_filter is not None:
            # Check symmetrical or directional rate
            bf_val = bf_lookup.get((start, end))
            if bf_val is None:
                # Fallback to symmetrical counterpart if not found
                bf_val = bf_lookup.get((end, start))

            if bf_val is not None and bf_val < float(bf_threshold):
                # Skip this route as it does not pass the user's threshold filter
                continue
                
            if bf_val is not None:
                properties['bayes_factor'] = bf_val
        
        # Create simple LineString representation for the arc
        line_geom = geojson.LineString([
            [start_lon, start_lat],
            [end_lon, end_lat]
        ])
        
        features.append(geojson.Feature(geometry=line_geom, properties=properties))
        
    return geojson.FeatureCollection(features)
