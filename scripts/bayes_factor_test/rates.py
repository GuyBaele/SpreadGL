import argparse
import math
import pandas as pd
import numpy as np


def main():
    welcome = "You can use this tool to perform Bayes factor test of significant diffusion rates on the BEAST log of discrete phylogeographic inference."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--log', '-lg', required=True,
                        help='Specify the input BEAST log file (.log).')
    parser.add_argument('--location', '-lo', required=True,
                        help='Type in the annotation that stores the location names in the MCC tree, e.g. "region".')
    parser.add_argument('--list', '-li', required=True,
                        help='Use the same location list from your discrete analysis as an input (.csv).')
    parser.add_argument('--layer', '-la', required=True,
                        help='Use the file of discrete spatial layer as an input (.csv).')

    args = parser.parse_args()
    log = str(args.log)
    location = str(args.location)
    list = str(args.list)
    layer = str(args.layer)

    def parse_bayes_factors(indicators, location_list, poisson_prior_mean=math.log(2), poisson_prior_offset=None):
        bayes_factor = []
        n = len(location_list)
        nrow = len(indicators)
        ncol = len(indicators[0])
        symmetrical = False

        if ncol == n * (n - 1):
            symmetrical = False
        elif ncol == (n * (n - 1)) // 2:
            symmetrical = True
        else:
            n1 = (math.sqrt(4 * ncol + 1) + 1) / 2
            n2 = (math.sqrt(8 * ncol + 1) + 1) / 2
            raise Exception(f"Number of rate indicators ({ncol}) does not match the number of locations! Specify {n2:.2f} locations if the location exchange models is a symmetrical one, or {n1:.2f} for a non-symmetrical one.")

        if poisson_prior_offset is None:
            poisson_prior_offset = n - 1

        if symmetrical:
            qk = (poisson_prior_mean + poisson_prior_offset) / ((n * (n - 1)) // 2)
        else:
            qk = (poisson_prior_mean + poisson_prior_offset) / ((n * (n - 1)) // 1)

        prior_odds = qk / (1 - qk)
        pk = getColumnMeans(indicators)

        for row in range(len(pk)):
            if pk[row] == 1:
                bf = ((pk[row] - (1.0 / nrow)) / (1 - (pk[row] - (1.0 / nrow)))) / prior_odds
                print("Infinite bf has been corrected to:", bf)
            else:
                bf = (pk[row] / (1 - pk[row])) / prior_odds
            bayes_factor.append(bf)
        return bayes_factor, pk


    def getColumnMean(a, col):
        sum_col = sum([row[col] for row in a])
        return sum_col / len(a)


    def getColumnMeans(a):
        return [getColumnMean(a, col) for col in range(len(a[0]))]

    print("Started processing, please wait...")
    log_df = pd.read_csv(log, sep='\t')
    columns = log_df.columns
    filtered_columns = []
    starting_location = []
    ending_location = []
    for column in columns:
        name_elements = column.split('.')
        if set([location,'indicators']).issubset(set(name_elements)):
            filtered_columns.append(column)
            ending_location.append(name_elements[-1])
            starting_location.append(name_elements[-2])
    log_df = log_df.loc[:, filtered_columns]
    indicators = log_df.values

    location_df = pd.read_csv(list)
    location_list = np.asarray(location_df['location'])

    bayes_factor, posterior_probability = parse_bayes_factors(indicators, location_list)
    bayes_df = pd.DataFrame({f'starting_{location}_name': starting_location, f'ending_{location}_name': ending_location,
                            'bayes_factor': bayes_factor, 'posterior_probability': posterior_probability})

    spread_df = pd.read_csv(layer)
    result_df = pd.merge(spread_df, bayes_df, how='left', on=[f'starting_{location}_name', f'ending_{location}_name'])
    result_df.to_csv(f'{log}.Bayes.factor.test.csv', sep=',', index=False)
    print(f'The result has been successfully stored as "{log}.Bayes.factor.test.csv" in the current directory!')    
        

# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
