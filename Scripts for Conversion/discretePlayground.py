from TreeParser import *
from discreteMCCTreeParser import *
from geojsonLayer import *


tree_path = input('Enter the entire path of your MCC tree file:')
location_list = input('Enter the entire path of your list of coordinates. This file should be in the format of ".csv" with the separator of "," \n'
                      'and comprised of three columns with a specific header of "location,latitude,longitude"')
date_format = input('If the sequence names end with dates in either ISO 8601 or decimal format, type in "date" or "number" correspondingly. \n Your response:')
# You should make sure all the sequence names end with correct date information in either ISO 8601 or decimal format.
# If the date part in ISO format is not complete, the first day of the corresponding month or year will be applied.
coordinate_annotation = input('What is the name of the annotation for locations? \n Your response:') + '='
output_path = input('Enter your desired destination path of the output:') + '/output.geojson'
print("Processing, please wait...")

parsed_tree = parseTree(tree_path)
tree_info = parseDiscreteMCCTree(parsed_tree, location_list, date_format, coordinate_annotation)
geojson_output = createGeojsonLayer(parsed_tree, tree_info)
with open(output_path, 'w') as f:
    geojson.dump(geojson_output, f)
print("The result was successfully stored in your path!")
