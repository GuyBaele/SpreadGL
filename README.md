# Spread.gl - visualising pathogen dispersal in a high-performance browser application
Main development repository and webpage for spread.gl, hosting installation files, input data files and tutorials for several visualisation examples.

## Installation
Before start, make sure you have already installed Git, npm, and Python3 on your device.  
Please refer to the following links for installation:  
https://git-scm.com/book/en/v2/Getting-Started-Installing-Git  
https://docs.npmjs.com/downloading-and-installing-node-js-and-npm  
https://www.python.org/downloads

1. Clone Github repository in your working directory and then use npm to install the web application:
```
git clone git@github.com:GuyBaele/SpreadGL.git
cd SpreadGL
npm install
```
2. Go to https://mapbox.com, sign up for an account and create a Mapbox Access Token.  
You will need to associate your token with Spread.gl:
```
chmod +x addToken.js
./addToken.js <insert_your_token>
```
3. Start the project, which will open a browser window, as follows:
```
npm start
```
4. Note: In case of any problems running 'npm start', you may also have to install the 'assert' and 'url' packages:
```
npm install assert
npm install url
```
5. Open a new terminal at the same folder. Install SpreadTools to create legit input files for visualisation.  
More information about different scripts can be found in the README of the scripts folder.
```
cd scripts
python -m venv my_env
source my_env/bin/activate (Linux/Mac)
.\my_env\Scripts\activate (Windows)
python setup.py install
```

## Visualising a (phylo)geographical spread layer in spread.gl
Once you have started spread.gl, you will see a world map in your browser window. To add your own visualisation, click the 'Add Data' button and import the file with extension '.output.geojson' via drag-and-drop. Then, you need to follow these steps to create different types of visuals:  
1. Create a layer to display phylogenetic branches. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Arc' in Basic. When specifying the coordinate fields (latitude and longitude) and coloring the branches, the source and target should correspond to the starting and ending points, respectively. You can adjust other parameters, such as opacity and stroke, to customise the visualisation. Once completed, the phylogenetic tree branches will be rendered on this layer.
2. (Discrete phylogeography) Create a layer that reflects the cumulative numbers of phylogenetic nodes at different places. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Cluster' in Basic. Specify the coordinate fields (latitude & longitude) of the ending points. Choose a sequential colour bar and set the colours based on 'Point Count' (by default). The radius parameters can be adjusted to set an appropriate size for the clusters. After that, the clusters that represent the cumulative numbers will be displayed on this layer.  
(Continuous phylogeography) Create a layer that enables the differentiation of nodes and tips. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Point' in Basic. Specify the coordinate fields (latitude & longitude) of the ending points. In order to effectively distinguish between the nodes and tips, it is recommended to utilise a qualitative colour bar and set the colours based on the 'type' field. As a result, the internal nodes and external tips will be categorised into distinct colours, allowing for clear and unambiguous observation.  
(Continuous phylogeography with available HPD data) Create a contour layer to visually represent uncertainty. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Polygon' in Basic. Then, you will see a lot of tangled polygons. Hide the stroke colour, change the fill colour as you want and lower the opacity to clearly see all the inner polygons. When playing the animation, contours will gradually appear in chronological order.
3. Create an animation for the dispersal over time. You need to add a filter to your map by selecting 'Filters' from the navigation bar, then clicking 'Add Filter' and choosing the result dataset. You should then select a field on which to filter data, in this case, a timestamp called "ending_time". Once this filter is applied to the map, you can see a time bar at the bottom of the screen. Set a moving time window and then click the play button, you will be able to see the animation.

## Visualising an environmental data layer in spread.gl
1. Create an environmental layer after processing tabular data. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Polygon' in Basic. Fill the colours based on your desired field. You can also set the colour scale as quantize and lower the opacity to increase the contrast between this layer and the base map layer. It is also possible to hide the stroke, change its colour and width.
2. Create an environmental layer after processing raster data. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Point' in Basic. Specify the coordinate fields (latitude & longitude) with correct fields. Fill the colours based on your desired field. You can also set the colour scale as quantize and lower the opacity to increase the contrast between this layer and the base map layer. The radius parameters can be adjusted to reach a better effect when zooming in/out.

## Animation examples in spread.gl
In the 'inputdata' folder, you can find all the required input files for our the different visualisation examples, which are explained in more detail below. The example output videos we provide below were obtained through screen recording on Mac using Screenshot.

### SARS-CoV-2 lineage A.27 Worldwide
We here visualise one of the discrete phylogeographic analyses from Kaleta et al. (2022) [Antibody escape and global spread of SARS-CoV-2 lineage A.27](https://www.nature.com/articles/s41467-022-28766-y). We here list the steps to follow in spread.gl:
1. We first need to process the MCC tree file using the 'spread' command, which takes the following 4 arguments:  
--tree: Specify the name of your input tree file with filename extension.  
--time: Enter the date of the most recent tip. It can be either in the format of YYYY-MM-DD or decimal year. In this case, it is 2021-06-01.  
--location: Type in the annotation that stores the location information (names or coordinates). In this case, the "region" annotation stores the names of regions and countries.  
--list: Only compulsory for discrete space analysis. Use a location list with its filename extension as an input. This file should be in the csv format with a comma (",") separator and comprised of three columns with a specific header of "location,latitude,longitude".  
When this processing step is done, you should be able to see a file called 'A.27_worldwide.MCC.tree.output.geojson'. It represents the spatial layer.
```
spread --tree A.27_worldwide.MCC.tree --time 2021-06-01 --location region --list A.27.location.list.csv
```

2. We can now visualise the spatial layers in spread.gl using the steps explained above (see Section 'Visualising a (phylo)geographical spread layer in spread.gl').  

https://user-images.githubusercontent.com/74751786/221681883-46bc7d5c-efdb-439c-bfbb-98c5f12f11ff.mov

### Rabies virus (RABV) in the United States
1. Process the MCC tree file using the following command.
```
spread --tree RABV_US1_gamma_MCC.tree --time 2004-7 --location location1,location2
```
This step works in the similar way as the A.27 example. Please take notice of the "--location" argument:  
As there are two annotations (location1 & location2 in this case) to store coordinates, you need to enter them in the order of latitude and longitude with a comma (",") separator in between.

2. Follow the previous steps to reach different visuals of the spatial layers. You can set the time window of animation as incremental for better observation of dispersal in continuous space.  

https://user-images.githubusercontent.com/74751786/221672148-b5190444-cb32-4047-a395-ed2cc8427130.mov

### Porcine epidemic diarrhea virus (PEDV) in China
1. Process the MCC tree file using the following command.
```
spread --tree PEDV_China.MCC.tree --time 2019-12-14 --location location --list Involved_provincial_capital_coordinates.csv
```
This step works in the same way as the A.27 example.

2. Process tabular environmental data.  
You need to add swine trade data to the map of China. The dataset 'National_swine_stocks.csv' was obtained from the original study (He et al.). The China map was generated via this link (http://datav.aliyun.com/portal/school/atlas/area_selector). Use the following command:
```
polygons --map China_map.geojson --foreignkey name --data National_swine_stocks.csv --primarykey location --output Swine_stocks_on_map.geojson
```
This command executes the polygons.py script with 5 required arguments:  
--data: Use environmental data (.csv, comma-delimited).  
--primarykey: For the input dataset, find a primary key field which will be referred by the input map. In this case, it is the "location" column.  
--map: Specify the input boundary map (.geojson).  
--foreignkey: For the input map, find a foreign key variable that refers to the primary key field in the input dataset. In this case, it is "name" in the part of properties.  
--output: Give a name to the output environmental layer (.geojson).  
A GeoJSON file named 'Swine_stocks_on_map.geojson' will be generated to display the environmental layer.

3. We can now visualise the spatial and environmental layers together in spread.gl using the steps explained above (see Sections 'Visualising a (phylo)geographical spread layer in spread.gl' & 'Visualising an environmental data layer in spread.gl'). If you would like to add a custom base map style, you need to first create a custom map style on Mapbox Studio (https://studio.mapbox.com). An official manual can be found via this link (https://docs.mapbox.com/studio-manual/guides). Once completed, open the Base Map panel, click the add map style button to open the custom map style modal, paste in the mapbox style Url. Note that you need to paste in your mapbox access token if your style is not published.

https://user-images.githubusercontent.com/74751786/205175522-5f639239-79d6-48c4-a097-837df9e50fa6.mp4

### Yellow fever virus (YFV) in Brazil
1. Process the MCC tree file using the following command.
```
spread --tree YFV.MCC.tree --time 2019-04-16 --location location1,location2
```
This step works in the same way as the RABV example. As the tree annotations include the information about regions of highest posterior density (HPD), the relevant data will be saved in the output GeoJSON file automatically.

2. Process raster environmental data.  
You can download the raster environmental data & a GeoJSON boundary map via the following links respectively:  
https://www.worldclim.org/data/monthlywth.html  
https://www.geoboundaries.org/index.html#getdata  
In this case, we would like to visualise the maximum temperature. As this is monthly data, the mean value of all the months from the year 2010 to 2018 will be calculated automatically once you specify the folder that contains the environmental raster files.  
Regarding the boundary map, you will need to provide a GeoJSON file. Since we only wish to visualise a few Brazilian provinces (not the entire world), we can apply a mask to clip it with a list of locations of interest.  
```
raster --data wc2.1_2.5m_tmax --map geoBoundaries-BRA-ADM1.geojson --mask Involved_brazilian_states.txt --foreignkey shapeName --output brazil_region_maxtemp.csv
```
This command executes the raster.py script with 5 required arguments:  
--data: Enter the folder that contains raster data files (.tif).  
--map: Specify the input boundary map (.geojson).  
--mask: Use a list of locations / location IDs of interest as a mask (.txt, comma-delimited).  
--foreignkey: Find a foreign key variable in the map that refers to the mask.  
--output: Give a name to the output environmental layer (.csv).  
A CSV file called 'brazil_region_maxtemp.csv' will be created to show the environmental layer.

3. Follow the previous steps to get different visuals of the spatial and environmental layers. For the spatial layer, you can generate a contour layer. For the environmental layer, you will need to choose 'Point' instead of 'Polygon' as the basic layer type. See Sections 'Visualising a (phylo)geographical spread layer in spread.gl' & 'Visualising an environmental data layer in spread.gl' for more information.

https://user-images.githubusercontent.com/74751786/200294883-a1a28d8c-44c0-4a0a-ab89-b3d137e704f1.mp4

### SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England
1. Process the single tree file using the following command.
```
spread --tree B.1.1.7_England.single.tree --time 2021-01-12 --location coordinates --format csv
```
This step works in the same way as the RABV example. Please take notice of the following argument:  
--format: It is optional. If you want to check the output in a table, use "csv" in this argument. For this example, we need tabular data for further data wrangling.

2. Reproject coordinates. Due to the original tree file using the British National Grid coordinate reference system (CRS), which is not supported in spread.gl, you need to perform an additional step (using the file 'B.1.1.7_England.single.tree.output.csv' created in step 2) to convert it to another CRS (i.e., the World Geodetic System 1984; WGS84). Use the following command:
```
reprojection --input B.1.1.7_England.single.tree.output.csv --lat starting_coordinates_1,ending_coordinates_1 --lng starting_coordinates_2,ending_coordinates_2 --src 27700 --trg 4326 --output B.1.1.7_England.single.tree.output.reprojected.csv
```
This command executes the reprojection.py script with 6 required arguments: input csv file, field names of source latitudes (comma separator in between), field names of source longitudes (comma separator in between), source CRS, target CRS and output csv file. When this step is done, there will be a new file called 'B.1.1.7_England.single.tree.output.reprojected.csv'.

3. Remove geographic outliers. If you visualise the reprojected output file created in step 3, there will be many points that fall outside Endland. These outliers were caused by missing geographic data. To identify them, it becomes necessary to refer to a dataset file 'TreeTime_270221.csv', which is an analysis result from the original study (Kraemer et al.). This file contains the location information of each point, i.e. UTLA (Upper Tier Local Authorities in England). You will need to check if this value is empty or not. If it is NULL, that point will fall outside of England. Therefore, the corresponding row (branch) has to be removed. Use the following command:
```
trimming --input B.1.1.7_England.single.tree.output.reprojected.csv --key ending_coordinates_1_original --refer TreeTime_270221.csv --foreign endLat --null startUTLA,endUTLA --output B.1.1.7_England.single.tree.output.reprojected.cleaned.csv
```
This command executes the trimming.py script with 6 required arguments: input csv file, foreign key field name of input, reference csv file, foreign field name of reference, queried field(s) of reference (comma separator in between if needed), and output csv file. When this step is done, there will be a new file called 'B.1.1.7_England.single.tree.output.reprojected.cleaned.csv'.

4. Visualise the spatial layers in Spread.gl.  
Follow the previous steps to get different visuals of the spatial layers.  

https://user-images.githubusercontent.com/74751786/200294175-24cf3c0a-92c6-49b6-ad9d-ed5dd57fe60d.mp4
