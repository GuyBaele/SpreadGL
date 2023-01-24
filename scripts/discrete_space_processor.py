from tree_parser import *
from discrete_tree_handler import *
from geojson_file_generator import *


def process_discrete_phylogeography(tree, date, location, geo_info, location_list, extension):
    print("Processing, please wait...")
    tree_path = '../' + tree
    parsed_tree, labels, edges = parse_tree(tree_path)
    location_list = '../' + location_list
    tree_info = handle_discrete_tree(parsed_tree, labels, edges, location_list, date, location, geo_info)
    if extension == "csv":
        df = pd.DataFrame(tree_info)
        output_name = tree + '.output.csv'
        output_path = '../' + output_name
        with open(output_path, 'w') as f:
            df.to_csv(f, index=False)
        print('The result was successfully stored as "' + output_name + '" in your directory!')
    else:
        geojson_output = generate_geojson_file(parsed_tree, tree_info)
        output_name = tree + '.output.geojson'
        output_path = '../' + output_name
        with open(output_path, 'w') as f:
            geojson.dump(geojson_output, f)
        print('The result was successfully stored as "' + output_name + '" in your directory!')
