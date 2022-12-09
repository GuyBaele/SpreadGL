from TreeParser import *
from continuousMCCTreeParser import *
from geojsonLayer import *


tree_path = input('Enter the entire path of your MCC tree file:')
date_format = input('If the sequence names end with dates in either ISO 8601 or decimal format, type in "date" or "number" correspondingly.\n Your response:')
# You should make sure all the sequence names end with correct date information in either ISO 8601 or decimal format.
# If the date part in ISO format is not complete, the first day of the corresponding month or year will be applied.
coordinate_annotation = input('If latitudes and longitudes are annotated with "location1" and "location2" correspondingly, type in "two".\n'
                              'If they are stored in the same annotation called "coordinates", type in "one". \n Your response:')
output_path = input('Enter your desired destination path of the output:') + '/output.geojson'
print("Processing, please wait...")

parsed_tree = parseTree(tree_path)
tree_info = parseContinuousMCCTree(parsed_tree, date_format, coordinate_annotation)
geojson_output = createGeojsonLayer(parsed_tree, tree_info)
with open(output_path, 'w') as f:
    geojson.dump(geojson_output, f)
print("The result was successfully stored in your path!")
