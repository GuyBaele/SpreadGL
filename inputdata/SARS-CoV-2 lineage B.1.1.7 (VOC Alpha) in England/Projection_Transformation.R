library(sp)
input <- read.csv("Output_UK_Projection_1st.csv", header=TRUE, stringsAsFactors=FALSE)
coords_uk_start = data.frame(start_lon=input[, c("start_longitude")], start_lat=input[, c("start_latitude")])
coords_uk_end = data.frame(end_lon=input[, c("end_longitude")], end_lat=input[, c("end_latitude")])
coordinates(coords_uk_start) = c("start_lon", "start_lat")
coordinates(coords_uk_end) = c("end_lon", "end_lat")
uk_projection = CRS("+init=epsg:27700")
proj4string(coords_uk_start) = uk_projection
proj4string(coords_uk_end) = uk_projection
wgs84 = CRS("+init=epsg:4326")
coords_wgs84_start = spTransform(coords_uk_start, wgs84)
coords_wgs84_end = spTransform(coords_uk_end, wgs84)
coords_wgs84_start = coords_wgs84_start@coords
coords_wgs84_end = coords_wgs84_end@coords
coords_wgs84_start_end <-cbind(coords_wgs84_start, coords_wgs84_end)
output <-cbind(input, coords_wgs84_start_end)
write.csv(output,"Output_Converted_2nd.csv", row.names = FALSE)
