from spatial_layer_generator.continuous_tree_handler import *


def process_continuous_phylogeography(tree, mostRecentTip, location, extension):
    print("Started processing, please wait...")
    data_frame, feature_collection = handle_continuous_tree(tree, mostRecentTip, location)
    if extension == "csv":
        output = tree + '.output.csv'
        with open(output, 'w') as f:
            data_frame.to_csv(f, index=False)
    else:
        output = tree + '.output.geojson'
        with open(output, 'w') as f:
            geojson.dump(feature_collection, f)
    print('The result has been successfully stored as "' + output + '" in the current directory!')
