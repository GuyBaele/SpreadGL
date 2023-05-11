# Spread.gl - visualising pathogen dispersal in a high-performance browser application
Main development repository and webpage for spread.gl, hosting installation files, input data files, example output and tutorials for several visualisation examples.

## Installation
Before starting, make sure you have already installed git, npm, and python3 on your device.  
We refer to the following links for installation instructions regarding these tools:  
https://git-scm.com/book/en/v2/Getting-Started-Installing-Git  
https://docs.npmjs.com/downloading-and-installing-node-js-and-npm  
https://www.python.org/downloads

1. Clone this Github repository in your working directory and use npm to install the web application:
```
git clone git@github.com:GuyBaele/SpreadGL.git
cd SpreadGL
npm install
```
2. Go to https://mapbox.com, sign up for an account and create a Mapbox Access Token.  
You will need to associate your token with spread.gl as follows:
```
chmod +x addToken.js
./addToken.js <insert_your_token>
```
3. Start the spread.gl visualisation, which will open a browser window, as follows:
```
npm start
```
4. Note: in case of any problems running 'npm start', you may first have to also install the 'assert' and 'url' packages, as follows:
```
npm install assert
npm install url
```
5. Open a new terminal in the SpreadGL directory. Install the provided spread.gl tools to create valid input files for your visualisations (additional information regarding the different scripts can be found in the README of the scripts directory):
```
cd scripts
python -m venv my_env
source my_env/bin/activate (Linux/Mac)
.\my_env\Scripts\activate (Windows)
python setup.py install
```

## Visualising a (phylo)geographical spread layer in spread.gl
Once you have started spread.gl, you will see a world map in your browser window. To add your own visualisation, click the 'Add Data' button and import the file with extension '.output.geojson' via drag-and-drop (see the sections below for how to generate .geojson files for your own analysis). Then, you need to follow these steps to create different types of visuals:  

1. Create a layer to display phylogenetic branches. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Arc' as the layer type in the Basic properties window. When specifying the coordinate fields (latitude and longitude) and coloring the branches, the source and target should correspond to the starting and ending points, respectively. You can adjust other parameters, such as opacity and stroke, to customise the visualisation. Once completed, the phylogenetic tree branches will be rendered on this layer.
2. (Discrete phylogeography) Create a layer that reflects the cumulative numbers of phylogenetic nodes at different places. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Cluster' in Basic. Specify the coordinate fields (latitude & longitude) of the ending points. Choose a sequential colour bar and set the colours based on 'Point Count' (by default). The radius parameters can be adjusted to set an appropriate size for the clusters. After that, the clusters that represent the cumulative numbers will be displayed on this layer.  
(Continuous phylogeography) Create a contour layer to visually represent uncertainty. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Polygon' in Basic. Then, you will see a lot of tangled polygons. Hide the stroke colour, change the fill colour as you want and lower the opacity to clearly see all the inner polygons. You can make the colour change automatically based on 'ending_time' and set the colour scale to quantize. When playing the animation, contours will gradually appear in chronological order.  
(Continuous phylogeography without available HPD data) This type of visualisation is meant for a single tree from a continuous phylogeographic analysis, i.e. not a consensus maximum clade credibility (MCC) tree. Create a layer that enables the differentiation of nodes and tips. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Point' in Basic. Specify the coordinate fields (latitude & longitude) of the ending points. In order to effectively distinguish between the nodes and tips, it is recommended to utilise a qualitative colour bar and set the colours based on the 'type' field. As a result, the internal nodes and external tips will be categorised into distinct colours, allowing for clear and unambiguous observation.
3. Create an animation for the dispersal over time. You need to add a filter to your map by expanding the panel of 'Filters' in the navigation bar and then doing 'Add Filter' on the spread layer. You should then select a field on which to filter data, in this case, a timestamp called "ending_time". Once this filter is applied to the map, you can see a time bar at the bottom of the screen. Set a moving time window and then click the play button, you will be able to see the animation.

## Visualising an environmental data layer in spread.gl
1. Create an environmental layer after processing tabular data. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Polygon' in Basic. Fill the colours based on your desired field. You can also set the colour scale as quantize and lower the opacity to increase the contrast between this layer and the base map layer. It is also possible to hide the stroke, change its colour and width.
2. Create an environmental layer after processing raster data. Select 'Layers' from the navigation bar, click 'Add Layer' and then choose 'Point' in Basic. Specify the coordinate fields (latitude & longitude) with correct fields. Fill the colours based on your desired field. You can also set the colour scale as quantize and lower the opacity to increase the contrast between this layer and the base map layer. The radius parameters can be adjusted to reach a better effect when zooming in/out.

## Animation examples in spread.gl
In the 'inputdata' folder, you can find all the required input files for our the different visualisation examples, which are explained in more detail below. The example output videos we provide below were obtained through screen recording on Mac using Screenshot.

### SARS-CoV-2 lineage A.27 Worldwide
We here visualise one of the discrete phylogeographic analyses from Kaleta et al. (2022) [Antibody escape and global spread of SARS-CoV-2 lineage A.27](https://www.nature.com/articles/s41467-022-28766-y). We here list the steps to follow in spread.gl:  

1. We first need to process the MCC tree file using the "spread" command, which takes the following 4 arguments:  
--tree: Specify the name of your input tree file with filename extension.  
--time: Enter the date of the most recent tip. It can be either in the format of YYYY-MM-DD or decimal year.  
  In this case, it is "2021-06-01".  
--location: Type in the annotation that stores the location information (names or coordinates).  
  In this case, the "region" annotation stores the names of regions and countries.  
--list: Only compulsory for discrete space analysis. Use a location list with its filename extension as an input. This file should be in the csv format with a comma (",") separator and comprised of three columns with a specific header of "location,latitude,longitude".  
--format: It is optional as the default format is GeoJSON. However, if you want to inspect the output in a table, you should type in "csv".  
When this processing step is done, you should be able to see a file called 'A.27_worldwide.MCC.tree.output.csv'. It represents the spatial layer.
```
spread --tree A.27_worldwide.MCC.tree --time 2021-06-01 --location region --list A.27.location.list.csv --format csv
```

2. We can now visualise the spatial layers in spread.gl using the steps explained above (see Section 'Visualising a (phylo)geographical spread layer in spread.gl').


https://user-images.githubusercontent.com/74751786/234103943-a2dab441-454d-4167-ac1d-a5b424ba7d97.mov


3. Perform a Bayes factor test.  
If you have a BEAST log file with rate indicators as described in Bayesian stochastic search variable selection (BSSVS), you can calculate the Bayes factors of diffusion rates for discrete phylogeographic analysis. The aim of this test is to identify rates that are frequently used to interpret the diffusion process.  
Use the command below to execute the 'rates.py' script with the following arguments:  
--log: Specify the input BEAST log file (.log).  
--location: Type in the annotation that stores the location names in the MCC tree, such as "region" in this case.  
--burnin: Specify burn-in to set how many initial samped values should be discarded from the analysis.  
It should be smaller than "1" but not less than "0", e.g. "0.1" should be sufficient for most analysis.  
You can also specify it by using the number of rows, which should be a valid integer in this case.  
--list: Use the same location list from your discrete analysis as an input (.csv).  
--layer: It is optional. You can combine the spatial layer with the Bayes factors. Use the file of discrete spatial layer as an input (.csv).  
The test result will be saved as 'Bayes.factor.test.result.csv'. If you specified the "layer" argument, a combined output called 'Bayes.factors.added.A.27_worldwide.MCC.tree.output.csv' will be generated for visualisation.
```
rates --log A.27_worldwide.BEAST.log --location region --burnin 0.1 --list A.27_worldwide_location_list.csv --layer A.27_worldwide.MCC.tree.output.csv
```

4. Set a filter with Bayes factors in visualisation.  
You can use the output file of Step 3 to filter the visualisation in Step 2. In spread.gl, add a new filter using the field of "bayes_factor". Then, set the left lower limit to "3.0" as a default cut-off value above which the diffusion rates are considered to be well supported. Only phylogenetic branches with a Bayes factor of at least 3 will be shown in the figure below. In addition, the clusters now only indicate cumulative counts of non-local transmissions.


<img width=100% alt="image" src="https://user-images.githubusercontent.com/74751786/234096466-3c452c36-2d42-4a9d-b2d6-ccc83a44941d.png">


### Rabies virus (RABV) in the United States
1. Process the MCC tree file using the command below. This step works in the similar way as the A.27 example.  
Please take notice of the "--location" argument: As there are two annotations (location1 & location2 in this case) to store coordinates, you need to enter them in the order of latitude and longitude with a comma (",") separator in between.
```
spread --tree RABV_US1_gamma_MCC.tree --time 2004-7 --location location1,location2
```

2. Follow the previous steps to reach different visuals of the spatial layers. You can set the time window of animation as incremental for better observation of dispersal in continuous space.


https://user-images.githubusercontent.com/74751786/230362590-db7320f9-893c-4997-b7bf-22744d7c4cb8.mov


### Porcine epidemic diarrhea virus (PEDV) in China
1. Process the MCC tree file using the following command. This step works in the same way as the A.27 example.
```
spread --tree PEDV_China.MCC.tree --time 2019-12-14 --location location --list Involved_provincial_capital_coordinates.csv
```

2. Process tabular environmental data.  
You need to add swine trade data to the map of China. The dataset 'National_swine_stocks.csv' was obtained from the original study (He et al.). The China map was generated via this link (http://datav.aliyun.com/portal/school/atlas/area_selector).  
Use the command below to execute the 'regions.py' script with 5 required arguments:  
--map: Specify the input boundary map in GeoJSON format (.geojson).  
--locationVariable: In the GeoJSON input file, find the property that represents the location variable.  
  In the 'China_map.geojson' file, each location is stored in a "name" variable (as part of the "properties").  
--data: Specify the environmental data you want to visualise in an environmental layer (.csv, comma-delimited).  
--locationColumn: In the CSV file, find the column that holds the location information.  
  In the 'National_swine_stocks.csv' file, this is the "location" column.  
--output: Give a file name in which to store the output environmental layer (.geojson).  
A GeoJSON file named 'Swine_stocks_on_map.geojson' will then be generated to display the environmental layer.
```
regions --map China_map.geojson --locationVariable name --data National_swine_stocks.csv --locationColumn location --output Swine_stocks_on_map.geojson
```

3. We can now visualise the spatial and environmental layers together in spread.gl using the steps explained above (see Sections 'Visualising a (phylo)geographical spread layer in spread.gl' & 'Visualising an environmental data layer in spread.gl'). If you would like to add a custom base map style, you need to first create a custom map style on Mapbox Studio (https://studio.mapbox.com). An official manual can be found via this link (https://docs.mapbox.com/studio-manual/guides). Once completed, open the Base Map panel, click the "Add Map Style" button to open the custom map style modal, paste in the mapbox style Url. Note that you need to paste in your mapbox access token if your style is not published.


https://user-images.githubusercontent.com/74751786/234107195-a03f8b47-dce0-4b06-9363-a4fc6c53a9a7.mov


### Yellow fever virus (YFV) in Brazil
1. Process the MCC tree file using the command below. This step works in the same way as the RABV example.  
As the tree annotations include the information about regions of highest posterior density (HPD), the relevant data will be saved in the output GeoJSON file automatically.
```
spread --tree YFV.MCC.tree --time 2019-04-16 --location location1,location2
```

2. Process raster environmental data.  
You can download the raster environmental data & a GeoJSON boundary map via the following links respectively:  
https://www.worldclim.org/data/monthlywth.html  
https://www.geoboundaries.org/index.html#getdata  
In this case, we would like to visualise the maximum temperature. As this is monthly data, the mean value of all the months from the year 2010 to 2018 will be calculated automatically once you specify the folder that contains the environmental raster files.  
Regarding the boundary map, you will need to provide a GeoJSON file. Since we only wish to visualise a few Brazilian provinces (not the entire world), we can apply a mask to clip it with a list of locations of interest.  
Use the command below to execute the 'raster.py' script with 5 required arguments:  
--data: Enter the folder that contains raster data files (.tif).  
--map: Specify the input boundary map (.geojson).  
--mask: Use a list of locations / location IDs of interest as a mask (.txt, comma-delimited).  
--foreignkey: Find a foreign key variable in the map that refers to the mask.  
--output: Give a name to the output environmental layer (.csv).  
A CSV file called 'brazil_region_maxtemp.csv' will then be created to show the environmental layer.
```
raster --data wc2.1_2.5m_tmax_2010-2018 --map geoBoundaries-BRA-ADM1.geojson --mask Involved_brazilian_states.txt --foreignkey shapeName --output brazil_region_maxtemp.csv
```

3. Follow the previous steps to get different visuals of the spatial and environmental layers. For the spatial layer, you can generate a contour layer. For the environmental layer, you will need to choose 'Point' instead of 'Polygon' as the basic layer type. See Sections 'Visualising a (phylo)geographical spread layer in spread.gl' & 'Visualising an environmental data layer in spread.gl' for more information.


https://user-images.githubusercontent.com/74751786/234108234-3b7b2887-0336-4713-93e7-6954776135fa.mov


### SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England
1. Process the single tree file using the command below. This step works in the same way as the RABV example.  
As we need tabular data for further data wrangling, do not forget to add the argument of "--format csv".  
```
spread --tree B.1.1.7_England.single.tree --time 2021-01-12 --location coordinates --format csv
```

2. Reproject coordinates.  
Due to the original tree file using the British National Grid coordinate reference system (CRS), which is not supported in spread.gl, you need to perform an additional step (using the file 'B.1.1.7_England.single.tree.output.csv' created in step 2) to convert it to another CRS (i.e., the World Geodetic System 1984; WGS84).  
Use the following command to execute the 'reprojection.py' script with 6 required arguments: input csv file, field names of source latitudes (comma separator in between), field names of source longitudes (comma separator in between), source CRS, target CRS and output csv file. When this step is done, there will be a new file called 'B.1.1.7_England.single.tree.output.reprojected.csv'.
```
reprojection --input B.1.1.7_England.single.tree.output.csv --lat starting_coordinates_1,ending_coordinates_1 --lng starting_coordinates_2,ending_coordinates_2 --src 27700 --trg 4326 --output B.1.1.7_England.single.tree.output.reprojected.csv
```

3. Remove geographic outliers.  
If you visualise the reprojected output file created in step 3, there will be many points that fall outside Endland. These outliers were caused by missing geographic data. To identify them, it becomes necessary to refer to a dataset file 'TreeTime_270221.csv', which is an analysis result from the original study (Kraemer et al.). This file contains the location information of each point, i.e. "UTLA" (Upper Tier Local Authorities in England). You will need to check if this value is empty or not. If it is "NULL", that point will fall outside of England. Therefore, the corresponding row (branch) has to be removed.  
Use the following command to execute the 'trimming.py' script with 6 required arguments: input csv file, foreign key field name of input, reference csv file, foreign field name of reference, queried field(s) of reference (comma separator in between, if needed), and output csv file. When this step is done, there will be a new file called 'B.1.1.7_England.single.tree.output.reprojected.cleaned.csv'.
```
trimming --input B.1.1.7_England.single.tree.output.reprojected.csv --key ending_coordinates_1_original --refer TreeTime_270221.csv --foreign endLat --null startUTLA,endUTLA --output B.1.1.7_England.single.tree.output.reprojected.cleaned.csv
```

4. Visualise the spatial layers in Spread.gl.  
Follow the previous steps to get different visuals of the spatial layers.


https://user-images.githubusercontent.com/74751786/230358490-38cdf607-e783-4fb4-8c98-8651eb69aaa5.mov

