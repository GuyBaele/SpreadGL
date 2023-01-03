from TreeParser import *
from discreteMCCTreeParser import *
from geojsonLayer import *


def processDiscreteMCCTree(tree, location_list, date, location, extension):
    print("Processing, please wait...")
    tree_path = '../' + tree
    parsed_tree = parseTree(tree_path)
    location_list = '../' + location_list
    tree_info = parseDiscreteMCCTree(parsed_tree, location_list, date, location)
    if extension == "csv":
        df = pd.DataFrame(tree_info)
        output_name = tree + '.output.csv'
        output_path = '../' + output_name
        with open(output_path, 'w') as f:
            df.to_csv(f, index=False)
        print('The result was successfully stored as "' + output_name + '" in your directory!')
    else:
        geojson_output = createGeojsonLayer(parsed_tree, tree_info)
        output_name = tree + '.output.geojson'
        output_path = '../' + output_name
        with open(output_path, 'w') as f:
            geojson.dump(geojson_output, f)
        print('The result was successfully stored as "' + output_name + '" in your directory!')
