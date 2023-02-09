from spatial_layer_generator.discrete_tree_handler import *


def process_discrete_phylogeography(tree, location, location_list, extension):
    print("Started processing, please wait...")
    data_frame, feature_collection = handle_discrete_tree(tree, location, location_list)
    if extension == "csv":
        output = tree + '.output.csv'
        with open(output, 'w') as f:
            data_frame.to_csv(f, index=False)
    else:
        output = tree + '.output.geojson'
        with open(output, 'w') as f:
            geojson.dump(feature_collection, f)
    print('The result has been successfully stored as "' + output + '" in the current directory!')
