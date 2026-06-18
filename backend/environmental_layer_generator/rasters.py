import os
import rasterio
import numpy as np
import geopandas as gpd
import rioxarray
import glob
import pandas as pd
import argparse
import re
from datetime import datetime


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
    welcome = ("This tool converts multiple raster TIFF files into one CSV with a timestamp per file. "
               "It is designed for time-series climate data (e.g., WorldClim).")
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--data', '-d', required=True,
                        help='Enter the folder that contains raster data files (.tif).')
    parser.add_argument('--map', '-m', required=True,
                        help='Specify the input boundary map (.geojson).')
    parser.add_argument('--locationVariable', '-lv', required=True,
                        help='In the GeoJSON input map, find a property that represents the location variable.')
    parser.add_argument('--locationList', '-ll', required=True,
                        help='Provide a location list of interest (.txt, comma-delimited).')
    parser.add_argument('--output', '-o', required=True,
                        help='Name the output dynamic environment data layer (.csv).')

    args = parser.parse_args()
    data = str(args.data)
    map = str(args.map)
    locationVariable = str(args.locationVariable)
    locationList = str(args.locationList)
    output = str(args.output)

    print("Started processing, please wait...")
    current_path = os.getcwd()
    folder_path = os.path.join(current_path, data)
    tif_files = glob.glob(folder_path + '/*.tif')

    gdf = safe_read_file(os.path.join(current_path, map))
    with open(os.path.join(current_path, locationList), 'r') as file:
        locations = file.read().split(',')
    gdf_filtered = gdf.loc[gdf[locationVariable].isin(locations)]

    # Initialize lists to store flattened data
    x_coords, y_coords, values, timestamps = [], [], [], []

    for tif_file in tif_files:
        filename = os.path.basename(tif_file)
        
        # Robust regex to find YYYY-MM pattern (e.g., inside 'wc2.1_2.5m_tmax_2015-04.tif')
        # We look specifically for 4 digits, a hyphen, and 2 digits.
        m = re.search(r'(\d{4})-(\d{2})', filename)
        
        if m:
            year, month = int(m.group(1)), int(m.group(2))
            # Set day to 15th to represent the monthly mean
            dt = datetime(year, month, 15)
            timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            # Fallback: attempt to parse the whole filename if regex fails
            base = filename.split('.')[0]
            try:
                dt = pd.to_datetime(base)
                timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                print("Warning: No valid timestamp found for " + filename + ". Skipping file.")
                continue

        # Open and mask data
        raster = rioxarray.open_rasterio(tif_file, masked=True)
        clipped = raster.rio.clip(gdf_filtered.geometry, drop=True)
        masked = clipped.where(np.isfinite(clipped), np.nan)
        
        raster_data = masked.values.squeeze()
        transform = masked.rio.transform()
        
        # Handle cases where the clip results in a 3D array (band, y, x) vs 2D (y, x)
        if len(raster_data.shape) == 3:
             raster_data = raster_data[0]
             
        rows, cols = raster_data.shape

        # Iterate through pixels to extract valid data
        for row in range(rows):
            for col in range(cols):
                val = raster_data[row, col]
                if not np.isnan(val):
                    x, y = rasterio.transform.xy(transform, row, col)
                    x_coords.append(x)
                    y_coords.append(y)
                    values.append(val)
                    timestamps.append(timestamp_str)

    data_dict = {
        'longitude': x_coords, 
        'latitude': y_coords, 
        'value': values, 
        'timestamp': timestamps
    }
    df = pd.DataFrame(data_dict)
    df.to_csv(os.path.join(current_path, output), index=False)
    print('The result has been successfully stored as "' + output + '" in the current directory!')


# Run with command line arguments precisely when called directly
if __name__ == '__main__':
    main()