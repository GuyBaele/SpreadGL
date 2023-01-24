from time_conversion import *
from coordinate_conversion import *
from tree_processor import *


def handle_discrete_tree(parsed_tree, labels, edges, location_list, date, location, geo_info):
    clades = []
    counter = 0
    if geo_info != 'None':
        geo_info = '../' + geo_info
        df_geo = pd.read_csv(geo_info)

    for clade in parsed_tree.find_clades(order='postorder'):
        end_name = labels[counter]
        duration = edges[counter]
        details = clade.comment.split(',')
        # Extract and process time information
        start_time, end_time = process_time_info(date, end_name, duration)
        # Extract and process location information
        if geo_info == 'None':
            location_info = parse_locations_from_one_annotation(details, location)
        else:
            location_info = np.asarray(df_geo.iloc[counter].values)[0]
        end_latitude, end_longitude = fetch_coordinates_from_location_list(location_info, location_list)
        counter += 1
        clade_info = {'id': counter, 'visited_times': 0, 'duration': duration, 'name': end_name, 'start_time': start_time, 'end_time': end_time,
                      'start_latitude': 0.0, 'start_longitude': 0.0, 'end_latitude': end_latitude, 'end_longitude': end_longitude}
        clades.append(clade_info)

    # DFS traverse the whole MCC tree to exchange information and infer values between tree branches
    iterate_tree(clades[::-1])

    for clade in clades:
        clade['start_time'] = convert_decimal_year_to_datetime(clade['start_time'])
        clade['end_time'] = convert_decimal_year_to_datetime(clade['end_time'])
        if clade['start_latitude'] == 0.0 and clade['start_longitude'] == 0.0:
            clade['start_latitude'] = clade['end_latitude']
            clade['start_longitude'] = clade['end_longitude']
        del clade['visited_times']

    return clades
