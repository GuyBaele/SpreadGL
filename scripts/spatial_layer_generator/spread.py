import argparse
from spatial_layer_generator.continuous_space_processor import *
from spatial_layer_generator.discrete_space_processor import *


def main():
    welcome = "Welcome to the spatial layer generator! You can create a spatial layer for a phylogenetic tree to display in Spread.gl."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--tree', '-tr', required=True,
                        help='Specify the filename (with extension) of your input tree file.')
    parser.add_argument('--time', '-ti', required=True,
                        help='Enter the date of the most recent tip. It can be either a formatted date or a decimal year.')
    parser.add_argument('--format', '-f',  choices=['YYYY-MM-DD', 'DD-MM-YYYY'], default='YYYY-MM-DD',
                        help='This OPTIONAL argument specifies the date format found at the end of phylogenetic tree taxa names. '
                             'The default format is "YYYY-MM-DD". It also supports "DD-MM-YYYY".')
    parser.add_argument('--location', '-lo', required=True,
                        help='Type in the annotation that stores the location information (names or coordinates). '
                             'If there are two annotations to store coordinates, enter them in the order of latitude and longitude with a comma separator.')
    parser.add_argument('--list', '-li',
                        help='Only compulsory for discrete space analysis. '
                             'Use a location list with its filename extension as an input. '
                             'This file should be in the csv format with a comma (",") separator, '
                             'and comprised of three columns with a specific header of "location,latitude,longitude".')
    parser.add_argument('--extension', '-e',  choices=['geojson', 'csv'], default='geojson',
                        help='This OPTIONAL argument specifies the output file extension. The default extension is "geojson". '
                             'It also supports "csv" to generate a table (without HPD polygons in case of continuous phylogeographic diffusion).')

    args = parser.parse_args()
    tree = str(args.tree)
    format = str(args.format)
    mostRecentTip = str(args.time)
    location = str(args.location).split(',')
    location_list = str(args.list)
    extension = str(args.extension)

    if location_list == 'None':
        process_continuous_phylogeography(tree, mostRecentTip, format, location, extension)
    else:
        process_discrete_phylogeography(tree, mostRecentTip, format, location, location_list, extension)


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
