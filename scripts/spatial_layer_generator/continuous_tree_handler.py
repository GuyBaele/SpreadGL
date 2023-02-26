import re
import geojson
import dendropy
import pandas as pd
from spatial_layer_generator.time_conversion import *
from spatial_layer_generator.branch_processor import *


def handle_continuous_tree(tree, mostRecentTip, location):
    tree = dendropy.Tree.get(path=tree, schema='nexus', preserve_underscores=True)
    delimiter = re.compile(r'[|\_]+')
    no_height = True
    not_root = False
    branches = []
    contours = []
    id = 0

    if type(mostRecentTip) == str:
        mostRecentTipDate = convert_datetext_to_datetime(mostRecentTip)
        mostRecentTipTime = convert_datetime_to_decimal_year(mostRecentTipDate)
    elif type(mostRecentTip) == float:
        mostRecentTipTime = mostRecentTip

    for edge in tree.preorder_edge_iter():
        id += 1
        branch_type = 'Internal'
        branch_length = edge.length if edge.length else 0.0
        # Parse time
        ending_time = 0.0
        starting_time = 0.0
        child_node = edge.head_node
        if child_node.is_leaf():
            branch_type = 'External'
            for annotation in child_node.annotations:
                if annotation.name == 'height':
                    no_height = False
                    ending_time = mostRecentTipTime - float(annotation.value)
                    starting_time = ending_time - branch_length
            if no_height:
                label = child_node.taxon.label
                name_elements = re.split(delimiter, label)
                ending_date = convert_datetext_to_datetime(name_elements[-1])
                ending_time = convert_datetime_to_decimal_year(ending_date)
                starting_time = ending_time - branch_length
        branch = dict(visited_times=0, id=id, type=branch_type, branch_length=branch_length, starting_time=starting_time, ending_time=ending_time)
        # Parse location
        parent_node = edge.tail_node
        if not_root:
            starting_annotation = parent_node.annotations
            for annotation in starting_annotation:
                if len(location) == 1 and annotation.name == location[0]:
                    branch['starting_'+location[0]+'_1'] = float(annotation.value[0])
                    branch['starting_'+location[0]+'_2'] = float(annotation.value[1])
                if len(location) == 2:
                    if annotation.name == location[0]:
                        branch['starting_'+location[0]] = float(annotation.value)
                    if annotation.name == location[1]:
                        branch['starting_'+location[1]] = float(annotation.value)
        ending_annotation = child_node.annotations
        contour_1, contour_2 = {}, {}
        for annotation in ending_annotation:
            if len(location) == 1 and annotation.name == location[0]:
                branch['ending_'+location[0]+'_1'] = float(annotation.value[0])
                branch['ending_'+location[0]+'_2'] = float(annotation.value[1])
            if len(location) == 2:
                if annotation.name == location[0]:
                    branch['ending_'+location[0]] = float(annotation.value)
                if annotation.name == location[1]:
                    branch['ending_'+location[1]] = float(annotation.value)
                if location[0] in annotation.name and 'HPD' in annotation.name:
                    contour_1[annotation.name] = annotation.value
                if location[1] in annotation.name and 'HPD' in annotation.name:
                    contour_2[annotation.name] = annotation.value
        # Parse contours if available
        polygons = []
        if contour_2 and contour_1:
            for key_2 in contour_2.keys():
                for key_1 in contour_1.keys():
                    if key_2[-1] == key_1[-1]:
                        value_2 = contour_2.get(key_2)
                        coordinates_2 = [float(i) for i in value_2]
                        value_1 = contour_1.get(key_1)
                        coordinates_1 = [float(i) for i in value_1]
                        linear_ring = list(zip(coordinates_2, coordinates_1))
                        polygon = geojson.Polygon([linear_ring])
                        polygons.append(polygon)
        branch.update({'contours': polygons})    
        branches.append(branch)
        not_root = True

    iterate_tree(branches)

    for branch in branches:
        del branch['visited_times']
        branch['starting_time'] = convert_decimal_year_to_datetime(branch['starting_time'])
        branch['ending_time'] = convert_decimal_year_to_datetime(branch['ending_time'])
        if branch['branch_length'] == 0.0:
            if len(location) == 1:
                branch['starting_'+location[0]+'_1'] = branch['ending_'+location[0]+'_1']
                branch['starting_'+location[0]+'_2'] = branch['ending_'+location[0]+'_2']
            if len(location) == 2:
                branch['starting_'+location[0]] = branch['ending_'+location[0]]
                branch['starting_'+location[1]] = branch['ending_'+location[1]]
        if branch['contours']:
            for polygon in branch['contours']:
                contour = geojson.Feature(geometry=polygon, properties={k: v for k, v in branch.items() if k != 'contours'})
                contours.append(contour)
        else:
            contour = geojson.Feature(geometry=geojson.Polygon([]),properties={k: v for k, v in branch.items() if k != 'contours'})
            contours.append(contour)
        del branch['contours']

    data_frame = pd.DataFrame(branches)
    contour_collection = geojson.FeatureCollection(contours)
    return data_frame, contour_collection
