import geojson
import re


def createGeojsonLayer(parsed_tree, tree_info):

    features = []
    tree_info_id = 0

    for clade in parsed_tree.find_clades():

        details = clade.comment.split('},')
        loc_1 = {}
        loc_2 = {}
        polygons = []

        for item in details:
            if 'location1_80%HPD' in item:
                location1_80HPD = re.search('(location1_80%HPD).*', item).group(0)
                loc1_header = re.compile(r'.+?(?=\=)').findall(location1_80HPD)[0]
                loc1_body = re.compile(r'(?<=\{)(.*)[^\}]+').findall(location1_80HPD)[0]
                loc_1[loc1_header] = loc1_body
            if 'location2_80%HPD' in item:
                location2_80HPD = re.search('(location2_80%HPD).*', item).group(0)
                loc2_header = re.compile(r'.+?(?=\=)').findall(location2_80HPD)[0]
                loc2_body = re.compile(r'(?<=\{)(.*)[^\}]+').findall(location2_80HPD)[0]
                loc_2[loc2_header] = loc2_body

        if loc_2 and loc_1:
            for key_2 in loc_2.keys():
                for key_1 in loc_1.keys():
                    if key_2[-1] == key_1[-1]:
                        value_2 = loc_2.get(key_2).split(",")
                        coordinates_2 = [float(i) for i in value_2]
                        value_1 = loc_1.get(key_1).split(",")
                        coordinates_1 = [float(i) for i in value_1]
                        linear_ring = list(zip(coordinates_2, coordinates_1))
                        polygon = geojson.Polygon([linear_ring])
                        polygons.append(polygon)

        if polygons and tree_info_id != 0:
            for polygon in polygons:
                feature = geojson.Feature(geometry=polygon, properties=tree_info[tree_info_id])
                features.append(feature)
        else:
            feature = geojson.Feature(geometry=geojson.Polygon([]), properties=tree_info[tree_info_id])
            features.append(feature)
        tree_info_id += 1

    feature_collection = geojson.FeatureCollection(features)
    return feature_collection

