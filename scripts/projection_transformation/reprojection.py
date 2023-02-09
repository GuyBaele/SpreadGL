import argparse
import pandas as pd
from pyproj import *


def main():
    welcome = "Welcome to this tool for projection transformation! You can convert geographic data between different CRS."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--input', '-i', required=True,
                        help='Specify the comma-delimited input file with filename extension (.csv).')
    parser.add_argument('--lat', '-la', required=True,
                        help='Type in the field names of source latitudes with a comma separator.')
    parser.add_argument('--lng', '-ln', required=True,
                        help='Type in the field names of source longitudes with a comma separator.')
    parser.add_argument('--src', '-s', required=True,
                        help='Type in EPSG code of source CRS, e.g. 27700.')
    parser.add_argument('--trg', '-t', required=True,
                        help='Type in EPSG code of target CRS. e.g. 4326.')
    parser.add_argument('--output', '-o', required=True,
                        help='Create a name with filename extension (.csv) for the output file.')

    args = parser.parse_args()
    input_file = str(args.input)
    src_lat = str(args.lat).split(',')
    src_lng = str(args.lng).split(',')
    src_crs = 'EPSG:'+str(args.src)
    trg_crs = 'EPSG:'+str(args.trg)
    output_file = str(args.output)

    df = pd.read_csv(input_file, delimiter=",")
    transformer = Transformer.from_crs(src_crs, trg_crs)
    for i in range(len(src_lng)):
        df[src_lat[i]+'_original'], df[src_lng[i]+'_original'] = df[src_lat[i]], df[src_lng[i]]
        df[src_lat[i]], df[src_lng[i]] = transformer.transform(df[src_lng[i]].tolist(), df[src_lat[i]].tolist())
    df.to_csv(output_file, sep=",", index=False)
    print('The result has been successfully stored as "' + output_file + '" in the current directory!')


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
