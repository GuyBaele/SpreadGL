import argparse
import pandas as pd


def main():
    welcome = "Welcome to this tool for outlier detection! You can remove outliers of the current dataset by referring to another one."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--input', '-i', required=True,
                        help='Specify the comma-delimited input file with filename extension (.csv).')
    parser.add_argument('--key', '-k', required=True,
                        help='Enter the foreign key field name of the input dataset. '
                        'In the case of geographic outliers, it can be the latitude field of ending points.')
    parser.add_argument('--refer', '-r', required=True,
                        help='Specify the comma-delimited reference dataset with filename extension (.csv). ')
    parser.add_argument('--foreign', '-f', required=True,
                        help='Enter the foreign field name of the referenced dataset. '
                        'In the case of geographic outliers, it can be the latitude field of ending points.')
    parser.add_argument('--null', '-n', required=True,
                        help='Enter the queried field(s) of the referenced dataset, where NULL values will be recorded. '
                        'If there are multiple fields to be used in the NULL queries, use a comma separator in between.')
    parser.add_argument('--output', '-o', required=True,
                        help='Create a name with filename extension (.csv) for the output file.')

    args = parser.parse_args()
    reference_dataset = str(args.refer)
    queried_fields = str(args.null).split(',')
    foreign_field = str(args.foreign)
    input_file = str(args.input)
    foreign_key_field = str(args.key)
    output_file = str(args.output)

    print("Started processing, please wait...")
    # Load the reference dataset to a DataFrame.
    df1 = pd.read_csv(open(reference_dataset), delimiter=",")
    # Perform NULL queries on the specified fields.
    # In this case, it records the branches that have no information about UTLA (English Upper Tier Local Authorities).
    # The queried fields: 'startUTLA,endUTLA'.
    selected = df1[df1[[i for i in queried_fields]].isna().any(1)]
    # Get values of the foreign/referenced columns.
    # Foreign field in this case: 'endLat'.
    foreign = selected.loc[:, foreign_field].map("{:.5f}".format).to_numpy()

    # Load the input dataset to a DataFrame.
    df2 = pd.read_csv(open(input_file), delimiter=",")
    # Delete the rows of input dataset whose values in the foreign key column are equal to those in the selected rows of reference dataset.
    # Foreign key field in this case: 'end_latitude_original'.
    for i in range(len(df2)):
        if "{0:.5f}".format(df2.loc[i, foreign_key_field]) in foreign:
            df2.drop(i, inplace=True)

    # Create a CSV output file.
    df2.to_csv(output_file, sep=",", index=False)
    print('The result has been successfully stored as "' + output_file + '" in the current directory!')


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
