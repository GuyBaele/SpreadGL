# Spread.gl - Visualising Pathogen Dispersal in a High-performance Browser Application
Main development repository and webpage for spread.gl, hosting installation files and input data files for several visualisation examples.

# Installation
1. Clone Repository
```
git clone git@github.com:FlorentLee/SpreadGL.git
```
2. Install Packages
```
npm install
```
3. Sign up for a Mapbox account and create an access token at mapbox.com. Modify the file of 'mapbox.js' and insert your own token.
4. Start the Project
```
npm start
```

# Processing MCC Tree Files
1. Drag or copy the contents of the scripts folder to the directory where the maximum clade credibility (MCC) tree and its location list (optional) are situated. More information regarding the different scripts can be found in the README of the scripts folder.
2. Install the required python packages in a new terminal in the scripts folder. You only have to do it once.  
   Note: Please make sure that you have already installed Python 3 before this step. 
```
pip install -r requirements.txt
```
3. Check the descriptions of arguments.
```
python3 main.py --help
```
4. Process the MCC tree you want to visualise. For example, for each of the three visualisations shown below, these are the commands required (but see the scripts directory for more information).
```
python3 main.py --tree B.1.1.7_England.MCC.tree --date datetime --location coordinates --type csv
python3 main.py --tree YFV.MCC.tree --date datetime --location location1,location2
python3 main.py --tree PEDV_China.MCC.tree --date datetime --location location --list Capital_Coordinates_Involved_Provinces.csv
```

# Animation examples in spread.gl
In the 'inputdata' folder, you can find all the required input files for our 3 examples in the manuscript.

## SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England
After processing the tree file of 'B.1.1.7_England.MCC.tree' using the command line mentioned above, you will find a file called 'B.1.1.7_England.MCC.tree.output.csv'. As its CRS (British National Grid) is not supported in Spread.gl, you need to take the following steps to convert it to another CRS (WGS84).

1. Open a new terminal at the folder of 'SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England'.

2. Reproject coordinates using R.  
Note: Please make sure that you have already installed R before this step.
```
Rscript Projection_Transformation.R
```
<details>
<summary>CLICK ME to see the script & comments.</summary>

```
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
```
</details>

3. Remove geographical outliers using Python.
```
python3 Outlier_Detection.py
```
<details>
<summary>CLICK ME to see the script & comments.</summary>

```
import pandas as pd

# Load data from the CSV file to a DataFrame.
file1 = open("B.1.1.7_England_reprojected_output.csv")
df1 = pd.read_csv(file1, delimiter=",")
arr1 = []
arr2 = []
# Record the latitude values of the starting & ending points.
for i in range(len(df1)):
    arr1.append(df1.loc[i, "start_latitude"])
    arr2.append(df1.loc[i, "end_latitude"])

# Load metadata to a DataFrame.
file2 = open("metadata_for_check.csv")
df2 = pd.read_csv(file2, delimiter=",")
arr3 = []
arr4 = []
# Only keep the records without any information about UTLA (English Upper Tier Local Authorities).
for i in range(len(df2)):
    if pd.isnull(df2.loc[i, "startUTLA"]):
        arr3.append(df2.loc[i, "startLat"])
    if pd.isnull(df2.loc[i, "endUTLA"]):
        arr4.append(df2.loc[i, "endLat"])

# Make the comparison. Once the starting or ending points have no information regarding UTLA, the record of that branch will be dropped.
for i in range(len(arr1)):
    if arr1[i] in arr3 or arr2[i] in arr4:
        df1.drop(i, inplace=True)

# Clean the result and export the output as a CSV file using the name of 'B.1.1.7_England_final_output.csv'.
df1 = df1.drop(columns=['id', 'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude'])
df1.to_csv("B.1.1.7_England_final_output.csv", sep=",", index=False)
```
</details>

Now, you can load the file of 'B.1.1.7_England_final_output.csv' in Spread.gl. Feel free to customise the visualisation as you want.

https://user-images.githubusercontent.com/74751786/200294175-24cf3c0a-92c6-49b6-ad9d-ed5dd57fe60d.mp4

## Yellow fever virus in Brazil
Generate the file of 'brazil_region_maxtemp.csv' as a temperature layer. (To Be Continued)

https://user-images.githubusercontent.com/74751786/200294883-a1a28d8c-44c0-4a0a-ab89-b3d137e704f1.mp4

## Porcine epidemic diarrhea virus (PEDV) in China
1. Generate the file of 'Pig_Population_Involved_Provinces.geojson' as an environmental layer.(To Be Continued)
2. Add a custom map style created on your own via Mapbox (https://studio.mapbox.com).

https://user-images.githubusercontent.com/74751786/205175522-5f639239-79d6-48c4-a097-837df9e50fa6.mp4
