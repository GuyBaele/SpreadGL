import argparse
import pandas as pd
from pyproj import *


def main():
    welcome = "Use this tool to convert geographic data between different CRS."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--input', '-i', required=True,
                        help='Specify the comma-delimited input file with filename extension (.csv).')
    parser.add_argument('--lat', '-la', required=True,
                        help='Type in the field names of source latitudes with a comma separator.')
    parser.add_argument('--lon', '-lo', required=True,
                        help='Type in the field names of source longitudes with a comma separator.')
    parser.add_argument('--source', '-s', required=True,
                        help='Type in EPSG code of source CRS, e.g. 27700.')
    parser.add_argument('--target', '-t', required=True,
                        help='Type in EPSG code of target CRS. e.g. 4326.')
    parser.add_argument('--output', '-o', required=True,
                        help='Create a name with filename extension (.csv) for the output file.')

    args = parser.parse_args()
    input_file = str(args.input)
    lat_ori = str(args.lat).split(',')
    lon_ori = str(args.lon).split(',')
    source_crs = 'EPSG:'+str(args.source)
    target_crs = 'EPSG:'+str(args.target)
    output_file = str(args.output)

    print("Started processing, please wait...")
    df = pd.read_csv(input_file, delimiter=",")
    transformer = Transformer.from_crs(source_crs, target_crs)
    for i in range(len(lon_ori)):
        df[lat_ori[i]+'_original'], df[lon_ori[i]+'_original'] = df[lat_ori[i]], df[lon_ori[i]]
        df[lat_ori[i]], df[lon_ori[i]] = transformer.transform(df[lon_ori[i]].tolist(), df[lat_ori[i]].tolist())
    df.to_csv(output_file, sep=",", index=False)
    print('The result has been successfully stored as "' + output_file + '" in the current directory!')


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
