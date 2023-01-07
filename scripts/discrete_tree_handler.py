from time_conversion import *
from coordinate_conversion import *
from tree_processor import *


def handle_discrete_tree(parsed_tree, location_list, date, location):

    clades = []
    counter = 1
    for clade in parsed_tree.find_clades():
        end_name = str(clade.name)
        duration = float(0.0 if clade.branch_length is None else clade.branch_length)
        details = clade.comment.split(',')
        start_time = 0.0
        end_time = 0.0
        # Extract and process time information
        if date == 'datetime':
            start_time, end_time = get_time_info_by_datetime(end_name, duration)
        if date == 'float':
            start_time, end_time = get_time_info_by_float(end_name, duration)
        # Extract and process location information
        end_latitude, end_longitude = parse_coordinates_from_location_list(location_list, details, location)
        clade_info = {'id': counter, 'visited_times': 0, 'duration': duration, 'name': end_name, 'start_time': start_time, 'end_time': end_time,
                      'start_latitude': 0.0, 'start_longitude': 0.0, 'end_latitude': end_latitude, 'end_longitude': end_longitude}
        clades.append(clade_info)
        counter += 1

    # DFS traverse the whole MCC tree to exchange information and infer values between tree branches
    iterate_tree(clades)

    for clade in clades:
        clade['start_time'] = convert_decimal_year_to_datetime(clade['start_time'])
        clade['end_time'] = convert_decimal_year_to_datetime(clade['end_time'])
        if clade['start_latitude'] == 0.0 and clade['start_longitude'] == 0.0:
            clade['start_latitude'] = clade['end_latitude']
            clade['start_longitude'] = clade['end_longitude']
        del clade['visited_times']

    return clades
