import argparse
import pandas
import geopandas


def main():
    welcome = "You can use this tool to create environmental layers for tabular data."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--region', '-r', required=True,
                        help='Specify the GeoJSON file with filename extension as the region part of the environmental layer.')
    parser.add_argument('--key', '-k', required=True,
                        help='Enter the foreign key field of the GeoJSON file. '
                        'In this case, it can be "name" in the properties.')
    parser.add_argument('--data', '-d', required=True,
                        help='Specify the comma-delimited CSV file with filename extension as the data part of the environmental layer.')
    parser.add_argument('--foreign', '-f', required=True,
                        help='Enter the foreign/referenced field of the CSV file. '
                        'In this case, it can be the "location" column.')
    parser.add_argument('--output', '-o', required=True,
                        help='Create a name with filename extension (.geojson) for the output file.')

    args = parser.parse_args()
    region = str(args.region)
    key = str(args.key)
    data = str(args.data)
    foreign = str(args.foreign)
    output = str(args.output)

    # Load a geojson file
    gdf = geopandas.read_file(region)
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
