# Install the sp package to deal with spatial data in R.
list.of.packages <- c("sp")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
library(sp)
options(warn=-1)

main <- function() {
    args <- commandArgs(trailingOnly = TRUE)
    input_filename <- args[1]
    output_filename <- args[2]

    # Load data from the CSV file into a DataFrame.
    setwd('..')
    input <- read.csv(input_filename, header=TRUE, stringsAsFactors=FALSE)

    # Create two data frames for the coordinates of the starting & ending points.
    coords_uk_start = data.frame(start_lon=input[, c("start_longitude")], start_lat=input[, c("start_latitude")])
    coords_uk_end = data.frame(end_lon=input[, c("end_longitude")], end_lat=input[, c("end_latitude")])

    # Set spatial coordinates to create a Spatial object.
    coordinates(coords_uk_start) = c("start_lon", "start_lat")
    coordinates(coords_uk_end) = c("end_lon", "end_lat")

    # Assign a particular CRS to spatial data by referring to its EPSG code.
    uk_projection = CRS(SRS_string = "EPSG:27700")
    slot(coords_uk_start, "proj4string") = uk_projection
    slot(coords_uk_end, "proj4string") = uk_projection

    # Transform from one CRS (British National Grid) to another (WGS84).
    wgs84 = CRS(SRS_string = "EPSG:4326")
    coords_wgs84_start = spTransform(coords_uk_start, wgs84)
    coords_wgs84_end = spTransform(coords_uk_end, wgs84)

    # Get the results and combine them.
    coords_wgs84_start = coords_wgs84_start@coords
    coords_wgs84_end = coords_wgs84_end@coords
    coords_wgs84_start_end <-cbind(coords_wgs84_start, coords_wgs84_end)
    output <-cbind(input, coords_wgs84_start_end)

    # Export the output as a CSV file.
    write.csv(output, output_filename, row.names = FALSE)
    print("Completed!")
}

main()
