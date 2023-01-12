# Spread.gl - Visualising Pathogen Dispersal in a High-performance Browser Application
Main development repository and webpage for spread.gl, hosting installation files and input data files for several visualisation examples along with short tutorials and example output videos.

# Installation
1. Clone repository
```
git clone git@github.com:FlorentLee/SpreadGL.git
```
2. Install packages
```
npm install
```
3. Sign up for a Mapbox account and create an access token at mapbox.com.  
   Modify the file of 'mapbox.js' and insert your own token there.
4. Start the project
```
npm start
```

# Processing MCC tree files
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
python3 main.py --tree B.1.1.7_England.single.tree --date datetime --location coordinates --type csv
python3 main.py --tree YFV.MCC.tree --date datetime --location location1,location2
python3 main.py --tree PEDV_China.MCC.tree --date datetime --location location --list Capital_Coordinates_Involved_Provinces.csv
```

# Animation examples in spread.gl
In the 'inputdata' folder, you can find all the required input files for our 3 examples in the manuscript.

## SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England

1. Open a new terminal in the folder 'SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England'.

2. As mentioned before, we first process the tree file 'B.1.1.7_England.single.tree' using the following command:
```
python3 main.py --tree B.1.1.7_England.single.tree --date datetime --location coordinates --type csv
```
This command does the following: ...
When this processing step has completed, a file 'B.1.1.7_England.single.tree.output.csv' will have been created. Due to the original tree file 

As its CRS (British National Grid) is not supported in Spread.gl, you need to take the following steps to convert it to another CRS (WGS84).



3. Reproject coordinates using R.  
Note: Please make sure that you have already installed R before this step.
```
Rscript Projection_Transformation.R
```

3. Remove geographical outliers using Python.
```
python3 Outlier_Detection.py
```

Now, you can load the file of 'B.1.1.7_England_final_output.csv' in Spread.gl. Feel free to customise the visualisation as you want.

https://user-images.githubusercontent.com/74751786/200294175-24cf3c0a-92c6-49b6-ad9d-ed5dd57fe60d.mp4

## Yellow fever virus in Brazil
Generate the file of 'brazil_region_maxtemp.csv' as a temperature layer. (To Be Continued)

https://user-images.githubusercontent.com/74751786/200294883-a1a28d8c-44c0-4a0a-ab89-b3d137e704f1.mp4

## Porcine epidemic diarrhea virus (PEDV) in China
1. Generate the file of 'Pig_Population_Involved_Provinces.geojson' as an environmental layer. (To Be Continued)
2. Add a custom map style created on your own via Mapbox (https://studio.mapbox.com).

https://user-images.githubusercontent.com/74751786/205175522-5f639239-79d6-48c4-a097-837df9e50fa6.mp4
