import argparse
from continuousProcessor import *
from discreteProcessor import *


def main():
    welcome = "Welcome to this processing tool! You can convert MCC trees to acceptable input files for Kepler.gl."
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument('--tree', '-tr', required=True,
                        help='Specify the file name of your MCC tree with filename extension.')
    parser.add_argument('--date', '-d', choices=['decimal', 'yyyy-mm-dd'], required=True,
                        help='At the end of sequence names, find the date format. '
                             'If it is a decimal number, enter "decimal". '
                             'If it is ISO-8601 (Year-Month-Day), enter "yyyy-mm-dd". '
                             'When it is incomplete, the first day of the corresponding month or year will be applied.')
    parser.add_argument('--location', '-l', required=True,
                        help='Enter the two annotations, storing latitudes and longitudes in this order, with a comma separator. '
                             'If there is only one annotation that stores either coordinates or location names, enter this annotation without comma.')
    parser.add_argument('--list', '-li',
                        help='Optional: Specify the file name of your list of coordinates with filename extension. '
                             'This file should be in the format of ".csv" with the separator of "," '
                             'and comprised of three columns with a specific header of "location,latitude,longitude".')
    parser.add_argument('--type', '-t',  choices=['csv'], help='Optional: Type in "csv" if you would like to inspect your output file in a tabular format.')

    args = parser.parse_args()
    tree = str(args.tree)
    date = str(args.date)
    location = str(args.location).split(',')
    location_list = str(args.list)
    extension = str(args.type)

    if location_list == 'None':
        processContinuousMCCTree(tree, date, location, extension)
    else:
        processDiscreteMCCTree(tree, location_list, date, location, extension)


# Run with command line arguments precisely when called directly
# (rather than when imported)
if __name__ == '__main__':
    main()
