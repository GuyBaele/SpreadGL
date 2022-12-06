# Spread.gl
Main development repository for SpreadGL.


# Installation
1. Clone Repository\
git clone git@github.com:FlorentLee/SpreadGL.git

2. Install Packages\
npm install

3. Mapbox Access Token\
Sign up for a Mapbox account and create an access token at mapbox.com.\
Modify the file of mapbox.js and insert your own token by the following instructions.\
vi src/mapbox.js\
i\
MAKE THE CHANGE\
Press ESC\
:w\
:q\

4. Start\
npm start


# Animation examples in spread.gl

In the "inputdata" directory , you can find all the required input files for our 3 examples in the manuscript.

## SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England

https://user-images.githubusercontent.com/74751786/200294175-24cf3c0a-92c6-49b6-ad9d-ed5dd57fe60d.mp4


Processing Steps:
1. Parse 'B.1.1.7_England.MCC.tree' with correct attribute names and regular expressions of '\d+-?\d+-?\d+'(DATES) & '-?\d+\.?\d+'(LOCATIONS).
2. Reproject coordinates from 'Output_UK_Projection_1st.csv' to 'Output_WGS84_RConverted_2nd.csv' using 'Projection_Transformation.R'.
3. Combine two files mentioned above in Microsoft Excel to get 'Output_Combined_3rd.csv' for further check.
4. Remove outliers by referring to 'metadata_for_check.csv' via 'Outlier_Detection.py'.
5. Apply 'Final_Output_4th.csv' in Kepler.gl and customise visualisation.

## Yellow fever virus in Brazil

https://user-images.githubusercontent.com/74751786/200294883-a1a28d8c-44c0-4a0a-ab89-b3d137e704f1.mp4


Processing Steps:
1. Parse 'YFV.MCC.tree' with correct attribute names and regular expressions of '\d+-?\d+-?\d+'(DATES), '.+?(?=\=)' & '(?<=\{)(.*)[^\}]+'(POLYGONS).
2. Get 'YFV_Polygon_Layer.geojson' and visualise it with 'brazil_region_maxtemp.csv' in Kepler.gl.

## Porcine epidemic diarrhea virus (PEDV) in China

https://user-images.githubusercontent.com/74751786/205175522-5f639239-79d6-48c4-a097-837df9e50fa6.mp4


Processing Steps:
1. Parse 'PEDV_China.MCC.tree' with the regular expression of '\d+-?\d+-?\d+'(DATES) and the correct location reference to 'Capital_Coordinates_Involved_Provinces.csv'.
2. Load 'PEDV_China_Output.csv' and 'Pig_Population_Involved_Provinces.geojson' in Kepler.gl.
3. Add custom map style by creating your own map style at mapbox for example.
