import argparse
from spatial_layer_generator.continuous_space_processor import *
from spatial_layer_generator.discrete_space_processor import *


def main():
    welcome = "Welcome to the spatial layer generator! You can create a spatial layer for a phylogenetic tree to display in Spread.gl."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--tree', '-tr', required=True,
                        help='Specify the name of your input tree file with filename extension.')
    parser.add_argument('--time', '-ti', required=True,
                        help='Enter the date of the most recent tip. It can be either in the format of YYYY-MM-DD or decimal year.')
    parser.add_argument('--location', '-lo', required=True,
                        help='Type in the annotation that stores the location information (names or coordinates). '
                             'If there are two annotations to store coordinates, enter them in the order of latitude and longitude with a comma separator.')
    parser.add_argument('--list', '-li',
                        help='Only compulsory for discrete space analysis. '
                             'Use a location list with its filename extension as an input. '
                             'This file should be in the csv format with a comma (",") separator, '
                             'and comprised of three columns with a specific header of "location,latitude,longitude".')
    parser.add_argument('--format', '-f',  choices=['csv'],
                        help='It is optional. If you want to check the output in a table, use "csv" in this argument.')

    args = parser.parse_args()
    tree = str(args.tree)
    mostRecentTip = str(args.time)
    location = str(args.location).split(',')
    location_list = str(args.list)
    extension = str(args.format)

    if location_list == 'None':
        process_continuous_phylogeography(tree, mostRecentTip, location, extension)
    else:
        process_discrete_phylogeography(tree, mostRecentTip, location, location_list, extension)


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
