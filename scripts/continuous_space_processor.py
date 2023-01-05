from tree_parser import *
from continuous_tree_handler import *
from geojson_file_generator import *


def process_continuous_phylogeography(tree, date, location, extension):
    print("Processing, please wait...")
    tree_path = '../' + tree
    parsed_tree = parse_tree(tree_path)
    tree_info = handle_continuous_tree(parsed_tree, date, location)
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
