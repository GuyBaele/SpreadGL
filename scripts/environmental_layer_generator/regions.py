import argparse
import pandas
import geopandas


def main():
    welcome = "You can use this tool to create environmental layers using tabular data."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--map', '-m', required=True,
                        help='Specify the input boundary map in GeoJSON format (.geojson).')
    parser.add_argument('--locationVariable', '-lv', required=True,
                        help='In the GeoJSON input file, find the property that represents the location variable.')
    parser.add_argument('--data', '-d', required=True,
                        help='Specify the environmental data you want to visualise in an environmental layer (.csv, comma-delimited).')
    parser.add_argument('--locationColumn', '-lc', required=True,
                        help='In the CSV file, find the column that holds the location information.')
    parser.add_argument('--output', '-o', required=True,
                        help='Give a file name in which to store the output environmental layer (.geojson).')

    args = parser.parse_args()
    map = str(args.map)
    location_variable = str(args.locationVariable)
    data = str(args.data)
    location_column = str(args.locationColumn)
    output = str(args.output)
    
    print("Started processing, please wait...")
    gdf = geopandas.read_file(map)
    pdf = pandas.read_csv(data, delimiter=',')
    joined_gdf = gdf.merge(pdf, how='left', sort=True, left_on=location_variable, right_on=location_column)
    new_order = list(pdf.keys()) + list(gdf.keys())
    joined_gdf = joined_gdf[new_order]
    joined_gdf.to_file(output, driver='GeoJSON')
    print('The result has been successfully stored as "' + output + '" in the current directory!')


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
