# Spread.gl
Main development repository and webpage for spread.gl, hosting installation files and input data files for several visualisation examples.


# Installation
1. Clone Repository
* git clone git@github.com:FlorentLee/SpreadGL.git

2. Install Packages
* npm install

3. Sign up for a Mapbox account and create an access token at mapbox.com.
* Modify the file of mapbox.js and insert your own token there.

4. Start the Project
* npm start

# Processing MCC Tree Files
Note: Please make sure that you have already installed Python 3. 
1. Drag or copy the contents of the scripts folder to the directory where the maximum clade credibility (MCC) tree and its location list (optional) are situated. More information regarding the different scripts can be found in the README of the scripts folder.
2. Install the required python packages in a new terminal in the scripts folder. You only have to do it once.
* pip install -r requirements.txt
3. Check the descriptions of arguments.
* python3 main.py --help
4. Process the MCC tree you want to visualise. For example, for each of the three visualisations shown below, these are the commands required (but see the scripts directory for more information):
* python3 main.py --tree B.1.1.7_England.MCC.tree --date yyyy-mm-dd --location coordinates --type csv
* python3 main.py --tree YFV.MCC.tree --date yyyy-mm-dd --location location1,location2
* python3 main.py --tree PEDV_China.MCC.tree --date yyyy-mm-dd --location location --list Capital_Coordinates_Involved_Provinces.csv

# Animation examples in spread.gl

In the "inputdata" folder, you can find all the required input files for our 3 examples in the manuscript.

## SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England

https://user-images.githubusercontent.com/74751786/200294175-24cf3c0a-92c6-49b6-ad9d-ed5dd57fe60d.mp4

You can follow the next steps to convert the coordinates of 'Output_UK_Projection_1st.csv' to accepted format.\
Note: Please make sure that you have already installed R. 
1. Open a new terminal at the folder of 'SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England'
2. Reproject the coordinates from the British National Grid CRS to the WGS 84 CRS in R.
* Rscript Projection_Transformation.R
3. Remove outliers by referring to the metadata and then get the final output.
* python3 Outlier_Detection.py

## Yellow fever virus in Brazil

https://user-images.githubusercontent.com/74751786/200294883-a1a28d8c-44c0-4a0a-ab89-b3d137e704f1.mp4


To be continued:\
Generate the file of 'brazil_region_maxtemp.csv' as a temperature layer.

## Porcine epidemic diarrhea virus (PEDV) in China

https://user-images.githubusercontent.com/74751786/205175522-5f639239-79d6-48c4-a097-837df9e50fa6.mp4


To be continued:
1. Generate the file of 'Pig_Population_Involved_Provinces.geojson' as an environmental layer.
2. Add a custom map style created on your own via Mapbox (https://studio.mapbox.com).
