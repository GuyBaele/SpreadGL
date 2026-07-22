import os
import rasterio
import numpy as np
import geopandas as gpd
import rioxarray
import glob
import pandas as pd
import argparse


def safe_read_file(file_path):
    if str(file_path).lower().endswith(('.geojson', '.json')):
        import json
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'features' in data:
                gdf = gpd.GeoDataFrame.from_features(data['features'])
                gdf.set_crs("EPSG:4326", inplace=True)
                return gdf
        except Exception as e:
            print(f"Warning: safe_read_file custom loader failed ({e}). Falling back to geopandas.read_file.")
    return gpd.read_file(file_path)


def main():
    welcome = "You can use this tool to create an environmental layer with raster data."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--data', '-d', required=True,
                        help='Enter the folder that contains raster data files (.tif).')
    parser.add_argument('--map', '-m', required=True,
                        help='Specify the input boundary map (.geojson).')
    parser.add_argument('--locationVariable', '-lv', required=True,
                        help='In the GeoJSON input map, find a property that represents the location variable.')
    parser.add_argument('--locationList', '-ll',required=True,
                        help='Provide a location list of interest (.txt, comma-delimited).')
    parser.add_argument('--output', '-o', required=True,
                        help='Give a name to the output environmental data layer (.csv).')

    args = parser.parse_args()
    data = str(args.data)
    map = str(args.map)
    locationVariable= str(args.locationVariable)
    locationList= str(args.locationList)
    output = str(args.output)

    print("Started processing, please wait...")
    current_path = os.getcwd()
    folder_path = os.path.join(current_path, data)
    tif_files = glob.glob(folder_path + '/*.tif')
    tif_arrays = []
    for tif_file in tif_files:
        tif_data = rioxarray.open_rasterio(os.path.join(folder_path, tif_file))
        tif_arrays.append(tif_data)
    mean_array = np.mean(tif_arrays, axis=0, dtype=np.float64)
    mean_array_2D = np.squeeze(mean_array, axis=0)
    with rasterio.open(os.path.join(folder_path, tif_files[0])) as src:
        meta = src.meta
    with rasterio.open(os.path.join(current_path, 'mean.tif'), 'w', **meta) as dst:
        dst.write(mean_array_2D, 1)
    raster = rioxarray.open_rasterio(filename=os.path.join(current_path, 'mean.tif'), masked=True)

    gdf = safe_read_file(os.path.join(current_path, map))
    with open(os.path.join(current_path, locationList), 'r') as file:
        locations = file.read().split(',')
    gdf_filtered = gdf.loc[gdf[locationVariable].isin(locations)]
    clipped = raster.rio.clip(gdf_filtered.geometry)
    masked = clipped.where(np.isfinite(clipped), np.nan)
    masked.rio.to_raster(os.path.join(current_path, 'masked.tif'))

    with rasterio.open(os.path.join(current_path, 'masked.tif')) as src:
            raster_data = src.read(1)
            rows, cols = raster_data.shape
            transform = src.transform
            x_coords, y_coords, values = [], [], []
            for row in range(rows):
                for col in range(cols):
                    x, y = rasterio.transform.xy(transform, row, col)
                    x_coords.append(x)
                    y_coords.append(y)
                    values.append(raster_data[row, col])
            data = {'longitude': x_coords, 'latitude': y_coords, 'value': values}
            df = pd.DataFrame(data).dropna()
            df.to_csv(os.path.join(current_path, output), index=False)
            print('The result has been successfully stored as "' + output + '" in the current directory!')


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
