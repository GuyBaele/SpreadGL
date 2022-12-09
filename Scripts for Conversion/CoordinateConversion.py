from PatternManagement import *
from RandomCoordsGenerator import *
import pandas as pd
import numpy as np


def parseCoordinatesFromTwo(details):
    end_latitude = float(matchCoordinate.findall(''.join([item for item in details if 'location1=' in item]))[0])
    end_longitude = float(matchCoordinate.findall(''.join([item for item in details if 'location2=' in item]))[0])
    return end_latitude, end_longitude


def parseCoordinatesFromOne(details):
    for i in range(len(details)):
        if 'coordinates=' in details[i]:
            end_latitude = float(matchCoordinate.findall(details[i])[0])
            end_longitude = float(matchCoordinate.findall(details[i + 1])[0])
            return end_latitude, end_longitude


def parseCoordinatesFromList(location_list, details, coordinate_annotation):
    df_geo = pd.read_csv(location_list)
    location = matchQuotedString.findall(''.join([item for item in details if coordinate_annotation in item]))[0]
    # Pick up a random location just in case
    if "+" in location:
        locations = location.split('+')
        location = random.choice(locations)
    matched_location_info = np.asarray(df_geo.loc[df_geo['location'] == location].values)
    end_location_info = matched_location_info[0]
    end_latitude, end_longitude = end_location_info[1], end_location_info[2]
    return end_latitude, end_longitude
