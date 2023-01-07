from pattern_management import *
import pandas as pd
import numpy as np


def parse_coordinates_from_two_annotations(details, location):
    location1 = location[0] + '='
    location2 = location[1] + '='
    end_latitude = float(match_coordinate.findall(''.join([item for item in details if location1 in item]))[0])
    end_longitude = float(match_coordinate.findall(''.join([item for item in details if location2 in item]))[0])
    return end_latitude, end_longitude


def parse_coordinates_from_one_annotation(details, location):
    location = location[0] + '='
    for i in range(len(details)):
        if location in details[i]:
            end_latitude = float(match_coordinate.findall(details[i])[0])
            end_longitude = float(match_coordinate.findall(details[i + 1])[0])
            return end_latitude, end_longitude


def parse_coordinates_from_location_list(location_list, details, location):
    df_geo = pd.read_csv(location_list)
    location = location[0] + '='
    location_info = match_quoted_string.findall(''.join([item for item in details if location in item]))[0]
    # Pick up a random location just in case
    if "+" in location_info:
        locations = location_info.split('+')
        location_info = np.random.choice(locations)
    matched_location_info = np.asarray(df_geo.loc[df_geo['location'] == location_info].values)
    end_location_info = matched_location_info[0]
    end_latitude, end_longitude = end_location_info[1], end_location_info[2]
    return end_latitude, end_longitude
