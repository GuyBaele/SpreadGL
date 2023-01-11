# Install the sp package to deal with spatial data in R.
library(sp)
options(warn=-1)
    
# Load data from the CSV file into a DataFrame.
input <- read.csv("B.1.1.7_England.MCC.tree.output.csv", header=TRUE, stringsAsFactors=FALSE)
         
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
                      
# Export the output as a CSV file using the name of 'B.1.1.7_England_reprojected_output.csv'.
write.csv(output,"B.1.1.7_England_reprojected_output.csv", row.names = FALSE)
