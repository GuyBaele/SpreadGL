import argparse
import pandas
import geopandas


def main():
    welcome = "You can use this tool to create an environmental layer with tabular data."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--data', '-d', required=True,
                        help='Use environmental data (.csv, comma-delimited).')
    parser.add_argument('--primarykey', '-pk', required=True,
                        help='For the input dataset, find a primary key field which will be referred by the input map.')
    parser.add_argument('--map', '-m', required=True,
                        help='Specify the input boundary map (.geojson).')
    parser.add_argument('--foreignkey', '-fk', required=True,
                        help='For the input map, find a foreign key variable that refers to the primary key field in the input dataset.')
    parser.add_argument('--output', '-o', required=True,
                        help='Give a name to the output environmental layer (.geojson).')

    args = parser.parse_args()
    data = str(args.data)
    primary_key = str(args.primarykey)
    map = str(args.map)
    foreign_key = str(args.foreignkey)
    output = str(args.output)
    
    print("Started processing, please wait...")
    gdf = geopandas.read_file(map)
    pdf = pandas.read_csv(data, delimiter=',')
    joined_gdf = gdf.merge(pdf, left_on=foreign_key, right_on=primary_key)
    joined_gdf.to_file(output, driver='GeoJSON')
    print('The result has been successfully stored as "' + output + '" in the current directory!')


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
