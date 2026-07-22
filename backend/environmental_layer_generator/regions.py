import argparse
import pandas
import geopandas


def safe_read_file(file_path):
    if str(file_path).lower().endswith(('.geojson', '.json')):
        import json
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'features' in data:
                gdf = geopandas.GeoDataFrame.from_features(data['features'])
                gdf.set_crs("EPSG:4326", inplace=True)
                return gdf
        except Exception as e:
            print(f"Warning: safe_read_file custom loader failed ({e}). Falling back to geopandas.read_file.")
    return geopandas.read_file(file_path)


def main():
    welcome = "You can use this tool to create an environmental layer with tabular data."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--data', '-d', required=True,
                        help='Specify the environmental tabular data you want to visualise (.csv, comma-delimited).')
    parser.add_argument('--locationColumn', '-lc', required=True,
                        help='In the CSV file, find the column that stores the location information.')
    parser.add_argument('--map', '-m', required=True,
                        help='Specify the input boundary map in GeoJSON format (.geojson).')
    parser.add_argument('--locationVariable', '-lv', required=True,
                        help='In the GeoJSON input map, find a property that represents the location variable.')
    parser.add_argument('--output', '-o', required=True,
                        help='Give a name to the output environmental data layer (.geojson).')

    args = parser.parse_args()
    data = str(args.data)
    map = str(args.map)
    location_column = str(args.locationColumn)
    location_variable = str(args.locationVariable)
    output = str(args.output)
    
    print("Started processing, please wait...")
    gdf = safe_read_file(map)
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
