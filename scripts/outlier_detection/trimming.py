import argparse
import pandas as pd


def main():
    welcome = "Use this tool to remove outliers of the current dataset by referring to another one."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--referencing', '-ri', required=True,
                        help='Enter the name of a comma-delimited referening table with filename extension (.csv).')
    parser.add_argument('--foreignkey', '-fk', required=True,
                        help='Enter the foreign key field name of the referening table, e.g. "end_lat".')
    parser.add_argument('--referenced', '-rd', required=True,
                        help='Enter the name of a comma-delimited referenced dataset with filename extension (.csv).')
    parser.add_argument('--primarykey', '-pk', required=True,
                        help='Enter the primary key field name of the referenced dataset, e.g. "endLat".')
    parser.add_argument('--null', '-n', required=True,
                        help='Specify the queried field(s) in the referenced dataset where NULL values are recorded. '
                        'If multiple fields are involved in the NULL queries, use a comma separator in between.')
    parser.add_argument('--output', '-o', required=True,
                        help='Create a name with filename extension (.csv) for the output file.')

    args = parser.parse_args()
    referencing_dataset = str(args.referencing)
    foreign_key_field = str(args.foreignkey)
    referenced_dataset = str(args.referenced)
    primary_key_field = str(args.primarykey)
    queries = str(args.null).split(',')   
    output = str(args.output)

    print("Started processing, please wait...")
    # Load the referenced dataset to a DataFrame.
    df1 = pd.read_csv(open(referenced_dataset), delimiter=",")
    # Perform NULL queries on the specified fields.
    # In this case, it records the branches that have no information about UTLA (English Upper Tier Local Authorities).
    # The queried fields: 'startUTLA,endUTLA'.
    selected = df1[df1[[i for i in queries]].isna().any(1)]
    # Get values of the primary key column.
    # In this case, 'endLat' is the primary key field name.
    foreign = selected.loc[:, primary_key_field].map("{:.5f}".format).to_numpy()

    # Load the referencing dataset to a DataFrame.
    df2 = pd.read_csv(open(referencing_dataset), delimiter=",")
    # Delete the rows of referencing dataset whose values in the foreign key column are equal to those in the selected rows of referenced dataset.
    # In this case, 'end_lat' is the foreign key field.
    for i in range(len(df2)):
        if "{0:.5f}".format(df2.loc[i, foreign_key_field]) in foreign:
            df2.drop(i, inplace=True)

    # Create a CSV output file.
    df2.to_csv(output, sep=",", index=False)
    print('The result has been successfully stored as "' + output + '" in the current directory!')


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
