import os
import rasterio
import numpy as np
import geopandas as gpd
import rioxarray
import glob
import pandas as pd
import argparse


def main():
    welcome = "You can use this tool to create environmental layers for raster data."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--folder', '-f', required=True,
                        help='Enter the folder that contains raster data (.tif files).')
    parser.add_argument('--region', '-r', required=True,
                        help='Specify the GeoJSON file with filename extension as the region part of the environmental layer.')
    parser.add_argument('--mask', '-m', required=True,
                        help='Use a list of locations of interest with its filename extension as a mask. '
                             'This file should be in the txt format with a comma (",") separator.')
    parser.add_argument('--output', '-o', required=True,
                        help='Create a name with filename extension (.csv) for the output file.')

    args = parser.parse_args()
    folder = str(args.folder)
    region = str(args.region)
    mask= str(args.mask)
    output = str(args.output)

    current_path = os.getcwd()
    folder_path = os.path.join(current_path, folder)
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

    gdf = gpd.read_file(os.path.join(current_path, region))
    with open(os.path.join(current_path, mask), 'r') as file:
        location_list = file.read().split(',')
    gdf_filtered = gdf.loc[gdf.shapeName.isin(location_list)]
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
