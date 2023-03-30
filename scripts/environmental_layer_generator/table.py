import argparse
import pandas
import geopandas


def main():
    welcome = "You can use this tool to create environmental layers using tabular data."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--map', '-m', required=True,
                        help='Specify the input boundary map (.GeoJSON).')
    parser.add_argument('--key', '-k', required=True,
                        help='Enter the key field of the GeoJSON file. '
                        'In this case, it can be "name" in the properties.')
    parser.add_argument('--data', '-d', required=True,
                        help='Use environmental data (.csv, comma-delimited).')
    parser.add_argument('--foreign', '-f', required=True,
                        help='Enter the foreign field of the CSV file. '
                        'In this case, it can be the "location" column.')
    parser.add_argument('--output', '-o', required=True,
                        help='Give a name to the output environmental layer (.GeoJSON).')

    args = parser.parse_args()
    map = str(args.map)
    key = str(args.key)
    data = str(args.data)
    foreign = str(args.foreign)
    output = str(args.output)

    # Load a geojson file
    gdf = geopandas.read_file(map)
    # Load a CSV file
    pdf = pandas.read_csv(data, delimiter=',')
    # Combine
    joined_gdf = gdf.merge(pdf, left_on=key, right_on=foreign)
    # Export
    joined_gdf.to_file(output, driver='GeoJSON')
    print('The result has been successfully stored as "' + output + '" in the current directory!')


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
