from TimeConversion import *
from CoordinateConversion import *
from BranchInference import *


def parseDiscreteMCCTree(parsed_tree, location_list, date_format, coordinate_annotation):

    clades = []
    counter = 1
    for clade in parsed_tree.find_clades():
        end_name = str(clade.name)
        duration = float(0.0 if clade.branch_length is None else clade.branch_length)
        details = clade.comment.split(',')
        start_time = 0.0
        end_time = 0.0
        # Extract and process date information
        if date_format == 'date':
            end_time, start_time = dateToEndTime(end_name, duration)
        if date_format == 'float':
            end_time, start_time = floatToEndTime(end_name, duration)
        # Extract and process location information
        end_latitude, end_longitude = parseCoordinatesFromList(location_list, details, coordinate_annotation)
        clade_info = {'id': counter, 'visited_times': 0, 'duration': duration, 'name': end_name, 'start_time': start_time, 'end_time': end_time,
                      'start_latitude': 0.0, 'start_longitude': 0.0, 'end_latitude': end_latitude, 'end_longitude': end_longitude}
        clades.append(clade_info)
        counter += 1

    # DFS Traverse the whole MCC tree to correctly assign information
    iterateTree(clades)

    for clade in clades:
        clade['start_time'] = decimalToDateTime(clade['start_time'])
        clade['end_time'] = decimalToDateTime(clade['end_time'])
        if clade['start_latitude'] == 0.0 and clade['start_longitude'] == 0.0:
            clade['start_latitude'] = clade['end_latitude']
            clade['start_longitude'] = clade['end_longitude']
        del clade['visited_times']

    return clades
