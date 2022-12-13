# Spread.gl
Main development repository for SpreadGL.


# Installation
1. Clone Repository
* git clone git@github.com:FlorentLee/SpreadGL.git

2. Install Packages
* npm install

3. Sign up for a Mapbox account and create an access token at mapbox.com.
* Modify the file of mapbox.js and insert your own token there.

4. Start the Project
* npm start

# Processing Tree Files
1. Drag the folder of TreeProcessingTool to the directory where the MCC tree and its location list (optional) are situated.
2. Install required packages in a new terminal at the folder of TreeProcessingTool. You only have to do it once.
* pip install -r requirements.txt
3. Check the descriptions of arguments.
* python3 main.py --help
4. Process the corresponding tree.
* python3 main.py --tree B.1.1.7_England.MCC.tree --date yyyy-mm-dd --location coordinates
* python3 main.py --tree YFV.MCC.tree --date yyyy-mm-dd --location location1,location2
* python3 main.py --tree PEDV_China.MCC.tree --date yyyy-mm-dd --location location --list Capital_Coordinates_Involved_Provinces.csv

# Animation examples in spread.gl

In the "inputdata" folder, you can find all the required input files for our 3 examples in the manuscript.

## SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England

https://user-images.githubusercontent.com/74751786/200294175-24cf3c0a-92c6-49b6-ad9d-ed5dd57fe60d.mp4


To be continued:
1. Reproject coordinates from 'Output_UK_Projection_1st.csv' to 'Output_WGS84_RConverted_2nd.csv' using 'Projection_Transformation.R'.
2. Combine two files mentioned above in Microsoft Excel to get 'Output_Combined_3rd.csv' for further check.
3. Remove outliers by referring to 'metadata_for_check.csv' via 'Outlier_Detection.py' to get 'Final_Output_4th.csv'.

## Yellow fever virus in Brazil

https://user-images.githubusercontent.com/74751786/200294883-a1a28d8c-44c0-4a0a-ab89-b3d137e704f1.mp4


To be continued:
Generate the file of 'brazil_region_maxtemp.csv' as a temperature layer.

## Porcine epidemic diarrhea virus (PEDV) in China

https://user-images.githubusercontent.com/74751786/205175522-5f639239-79d6-48c4-a097-837df9e50fa6.mp4


To be continued:
1. Generate the file of 'Pig_Population_Involved_Provinces.geojson' as an environmental layer.
2. Add a customised map style created on your own, e.g. via Mapbox.
