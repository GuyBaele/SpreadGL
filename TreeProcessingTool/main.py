import argparse
from continuousProcessor import *
from discreteProcessor import *


def main():
    welcome = "Welcome to this processing tool! You can convert MCC trees to acceptable input files for Kepler.gl."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--tree', '-t', required=True,
                        help='Specify the name of your MCC tree file with filename extension.')
    parser.add_argument('--date', '-d', choices=['yyyy-mm-dd', 'decimal'], required=True,
                        help='At the end of sequence names, find the date format.'
                             'If it is ISO-8601 (Year-Month-Day), enter "yyyy-mm-dd". '
                             'When it is incomplete, the first day of the corresponding month or year will be applied.'
                             'If it is a decimal number, enter "decimal".')
    parser.add_argument('--location', '-l', required=True,
                        help='Enter the two annotations, where latitudes and longitudes are stored, with a comma separator.'
                             'If they is only one annotation that stores coordinates or location names, enter its name without comma.')
    parser.add_argument('--list', '-li',
                        help='Specify the name of your list of coordinates with filename extension.'
                             'This file should be in the format of ".csv" with the separator of ","'
                             'and comprised of three columns with a specific header of "location,latitude,longitude".')
    args = parser.parse_args()
    tree = str(args.tree)
    date = str(args.date)
    location = str(args.location).split(',')
    location_list = str(args.list)

    if location_list == 'None':
        processContinuousMCCTree(tree, date, location)
    else:
        processDiscreteMCCTree(tree, location_list, date, location)


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
