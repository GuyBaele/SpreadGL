# Spread.gl - Visualising Pathogen Dispersal in a High-performance Browser Application
Main development repository and webpage for spread.gl, hosting installation files and input data files for several visualisation examples along with short tutorials and example output videos.

## Installation
Before start, make sure you have already installed Git, npm, and Python3 in your device.  
Otherwise, please refer to the following links for installation.  
https://git-scm.com/book/en/v2/Getting-Started-Installing-Git  
https://docs.npmjs.com/downloading-and-installing-node-js-and-npm  
https://www.python.org/downloads

1. Clone Github repository in your working directory and then install packages.
```
git clone git@github.com:GuyBaele/SpreadGL.git
cd SpreadGL
npm install
```
2. Go to https://mapbox.com, sign up for an account and create a Mapbox Access Token. Then, you need to apply your token in Spread.gl.
```
chmod +x script.js
./addToken.js <insert_your_token>
```
3. Start the project, which will open a browser window.
```
npm start
```
Note: In case of any problems running 'npm start', you may also have to install the 'assert' and 'url' packages.
```
npm install assert
npm install url
```

## Processing MCC tree files
1. Install the processing toolkit. More information about different scripts can be found in the README of the scripts folder.
```
cd scripts
python3 setup.py install
```
2. Check the description of the main tool: spatial_layer_generator.
```
spatial --help
```
3. Process the MCC tree you want to visualise. For example, for each of the three visualisations shown below, these are the basic commands required (but see the examples below for more processing steps and the scripts directory for more detailed information).
```
spatial --tree B.1.1.7_England.single.tree --location coordinates --format csv
spatial --tree YFV.MCC.tree --location location1,location2
spatial --tree PEDV_China.MCC.tree --location location --list Involved_provincial_capital_coordinates.csv
```

## Animation examples in spread.gl
In the 'inputdata' folder, you can find all the required input files for our 3 examples in the manuscript.  
We also provide example output videos by recording the screen on Mac using Screenshot.

### SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England
1. Process the tree file using the following command:
```
spatial --tree B.1.1.7_England.single.tree --location coordinates --format csv
```
This command does the following: Execute the Python script of spatial.py with 3 arguments: input tree file, an annotation containing coordinates information, and the csv format of output file. When this step is done, a file 'B.1.1.7_England.single.tree.output.csv' will have been created.

2. Reproject coordinates. Due to the original tree file using the British National Grid coordinate reference system (CRS), which is not supported in spread.gl, you need to perform an additional step (using the file 'B.1.1.7_England.single.tree.output.csv' created in step 2) to convert it to another CRS (i.e., the World Geodetic System 1984; WGS84). Type in the following commands to check description and start execution:
```
reprojection --help
reprojection --input B.1.1.7_England.single.tree.output.csv --lat start_latitude,end_latitude --lng start_longitude,end_longitude --src 27700 --trg 4326 --output B.1.1.7_England.single.tree.output.reprojected.csv
```
This command does the following: Execute the Python script of reprojection.py with 6 required arguments: input csv file, field names of source latitudes (comma separator in between), field names of source longitudes (comma separator in between), source CRS, target CRS and output csv file. When this step is done, a file 'B.1.1.7_England.single.tree.output.reprojected.csv' will have been created.

3. Remove geographic outliers. If you visualise the reprojected output file created in step 3, there will be many points that fall outside Endland. These outliers were caused by missing geographic data. To identify them, it becomes necessary to refer to a dataset file 'TreeTime_270221.csv', which is an analysis result from the original study (Kraemer et al.). This file contains the location information of each point, i.e. UTLA (Upper Tier Local Authorities in England). You will need to check if this value is empty or not. If it is NULL, that point will fall outside of England. Therefore, the corresponding row(branch) has to be removed. Type in the following commands to check description and start execution:
```
trimming --help
trimming --input B.1.1.7_England.single.tree.output.reprojected.csv --key end_latitude_original --refer TreeTime_270221.csv --foreign endLat --null startUTLA,endUTLA --output B.1.1.7_England.single.tree.output.reprojected.cleaned.csv
```
This command does the following: Execute the Python script of trimming.py with 6 required arguments: input csv file, foreign key field name of input, reference csv file, foreign field name of reference, queried field(s) of reference (comma separator in between if needed), and output csv file. When this step is done, a file 'B.1.1.7_England.single.tree.output.reprojected.cleaned.csv' will have been created.

4. Visualise the end result.
Now, you can load the end result in Spread.gl in your browser. Click the buttom "Add Data". Drag & drop the file of 'B.1.1.7_England_final_output.csv' there. You can customise the visualisation by adjusting the parameters in the side panal, i.e. showing / hiding / creating / deleting / reordering / colouring different layers, adding the end_time as a filter to create animation, and applying your favourite map style, etc.

https://user-images.githubusercontent.com/74751786/200294175-24cf3c0a-92c6-49b6-ad9d-ed5dd57fe60d.mp4

### Yellow fever virus in Brazil
1. Process the tree file using the following command:
```
spatial --tree YFV.MCC.tree --location location1,location2
```
This command does the following: Execute the Python script of spatial.py with 2 arguments: input tree file and two annotations containing coordinates information (comma separator in between). When this step is done, a file 'YFV.MCC.tree.output.geojson' will have been created.

2. Generate the file of 'brazil_region_maxtemp.csv' as a temperature layer.  
(To Be Continued)

3. Visualise the spatial layer and the environmental layer together in Spread.gl.

https://user-images.githubusercontent.com/74751786/200294883-a1a28d8c-44c0-4a0a-ab89-b3d137e704f1.mp4

### Porcine epidemic diarrhea virus (PEDV) in China
1. Process the tree file using the following command:
```
spatial --tree PEDV_China.MCC.tree --location location --list Involved_provincial_capital_coordinates.csv
```
This command does the following: Execute the Python script of spatial.py with 3 arguments: input tree file, the annotation containing location (province) information, and a list of capital coordinates of involved provinces. When this step is done, a file 'PEDV_China.MCC.output.geojson' will have been created.

2. Create an environmental layer. You need to add swine trade data to the map of China. The dataset 'National_swine_stocks.csv' was obtained from the original study (He et al.). The China map was generated via this link (http://datav.aliyun.com/portal/school/atlas/area_selector). Type in the following commands to check description and start execution:
```
environmental --help
environmental --region China_map.geojson --key name --data National_swine_stocks.csv --foreign location --output Swine_stocks_on_map.geojson
```
This command does the following: Execute the Python script of environmental.py with 5 required arguments: input map (.GeoJSON), foreign key field name in the properties part of input, environmental data (.csv), foreign field name in data, and output map (.GeoJSON). When this step is done, a file 'Swine_stocks_on_map.geojson' will have been created.

3. Visualise the spatial layer and the environmental layer together in Spread.gl. To add a custom base map style, you need to create a custom map style on Mapbox Studio (https://studio.mapbox.com). An official manual can be found via this link (https://docs.mapbox.com/studio-manual/guides). Once completed, open the Base Map panel, click the add map style button to open the custom map style modal, paste in the mapbox style Url. Note that you need to paste in your mapbox access token if your style is not published.

https://user-images.githubusercontent.com/74751786/205175522-5f639239-79d6-48c4-a097-837df9e50fa6.mp4
