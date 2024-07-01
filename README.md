# spread.gl - visualising pathogen dispersal in a high-performance browser application
Main development repository and webpage for spread.gl, hosting installation files, input data files, example output and tutorials for several visualisation examples.

## Dockerised Quick Installation
Before you start, please install the latest version of [Docker Desktop](https://www.docker.com/products/docker-desktop/).
1. Download the codebase on the docker branch, unzip it and enter this folder.
2. Open a terminal in this directory and execute the following command to pull images and set up a container for them. To restart the container after exiting, rerun this command in the terminal of the same directory.  
```
docker-compose up -d
```
3. Access the webpage of Spread.gl in your favourite browser via a local host IP address: http://localhost:8080, or run:
```
open http://localhost:8080
```
4. The ‘inputdata’ folder is the default location to store all the input data files/subfolders.
   If you continue to save your data in this folder, run this command to start a backend interactive session in the terminal of the same directory.
```
docker-compose exec backend /bin/bash
```
(Optional) If you need to mount a local directory on your hard drive into the container, replace the "/FOLDER/PATH/TO/INPUT/DATA" part with an absolute path to your preferred data folder, and then run:
```
docker run -it --volume "/FOLDER/PATH/TO/INPUT/DATA":/backend florentlee/spread.gl.processing.toolkit:1.0.0 /bin/bash
```
5. Run this command to learn how to process input data.
```
spread -h
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
In the 'inputdata' folder, you can find most of the required input files (excluding environmental data in the YFV example) for our different visualisation examples, which are explained in more detail below. Certain files need to be unzipped before processing. The example output videos we provide below were obtained through screen recording on Mac using Screenshot.

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
When this processing step is done, you will see an output file of the spread layer called 'A.27_worldwide.MCC.tree.output.csv'.
```
spread --tree A.27_worldwide.MCC.tree --time 2021-06-01 --location region --list A.27_worldwide_location_list.csv --format csv
```

2. We can now visualise the spread layer in spread.gl using the steps explained above (see Section 'Visualising a (phylo)geographical spread layer in spread.gl').


https://github.com/GuyBaele/SpreadGL/assets/1092968/597c0b36-ffaa-44ad-97af-e128a646dcad


3. Perform a Bayes factor test.  
If you have a BEAST log file with rate indicators as a result of the Bayesian stochastic search variable selection (BSSVS) procedure, you will be able to calculate Bayes factors for the diffusion rates between the discrete locations. This test aims to identify relevant rates that are typically used to interpret the diffusion process. **Unzip** "A.27_worldwide.BEAST.log.zip" and execute the 'rates.py' script using the following command with different arguments:  
--log: Specify as input the BEAST log file (.log).  
--location: Type in the annotation that stores the location names in the MCC tree, i.e., "region" in this case.  
--burnin: Specify the burn-in ratio to set how many initial sampled values need to be discarded from the analysis. This number should be smaller than "1" but not less than "0", e.g. "0.1" should be sufficient for most analyses (but check your .log file in Tracer). An integer that represents the number of rows is also allowed.  
--list: Use the same location list from your discrete analysis as input (.csv).  
--layer: OPTIONAL; To combine the spread layer with Bayes factors, use the output from step 1 as input (.csv).  
The test result will be saved as 'Bayes.factor.test.result.csv'. If you specify the "layer" argument, a combined output file called 'Bayes.factors.added.A.27_worldwide.MCC.tree.output.csv' will be generated for visualisation.
```
rates --log A.27_worldwide.BEAST.log --location region --burnin 0.1 --list A.27_worldwide_location_list.csv --layer A.27_worldwide.MCC.tree.output.csv
```

4. Set a filter with Bayes factors in visualisation.  
To filter the visualisation in step 2, delete the current dataset in spread.gl and load the output file of step 3. In the Filters panel, add a new filter using the field "bayes_factor". Subsequently, set the left lower limit to "3.0" as a default cut-off value above which the diffusion rates are considered to be well supported. Only phylogenetic branches with a Bayes factor of at least 3 will be shown in the figure below. In addition, the clusters now only indicate cumulative counts of non-local transmissions.

<img width=100% alt="image" src="https://user-images.githubusercontent.com/74751786/234096466-3c452c36-2d42-4a9d-b2d6-ccc83a44941d.png">


### Rabies virus (RABV) in the United States
We perform the following steps to visualise one of the continuous phylogeographic analyses from Biek et al. (2007) [A high-resolution genetic signature of demographic and spatial expansion in epizootic rabies virus](https://www.pnas.org/doi/full/10.1073/pnas.0700741104). This is an example for which the MCC tree does not have the HPD information for the ancestral locations.  
1. Process the MCC tree file using the command below. This step works in a similar way as the A.27 example.  
Please take notice of the "--location" argument: As there are two annotations (location1 & location2 in this case) to store coordinates, you need to enter them in the order of latitude and longitude with a comma (",") separator in between.
```
spread --tree RABV_US1_gamma_MCC.tree --time 2004-7 --location location1,location2
```

2. Follow the previous steps to try different visuals of the spread layer. Please pay attention to the "continuous phylogeography without HPD" part of Section 'Visualising a (phylo)geographical spread layer in spread.gl'. You can set the time window of animation as incremental for better observation of dispersal in continuous space.


https://github.com/GuyBaele/SpreadGL/assets/1092968/e19685f5-1107-4a66-8165-78443b8a745d


### Porcine epidemic diarrhea virus (PEDV) in China
1. Process the MCC tree file using the following command. This step works in the same way as the A.27 example.
You should be able to get an output file of the spread layer, named 'PEDV_China.MCC.tree.output.geojson' and used in step 3.
```
spread --tree PEDV_China.MCC.tree --time 2019-12-14 --location location --list Involved_provincial_capital_coordinates.csv
```

2. Use tabular environmental data to populate vector data.  
In this example, we need to add environmental table data to the GeoJSON map.  
The tabular dataset, 'Environmental_variables.csv', can be obtained from the original study conducted by He et al. (2021) [Phylogeography Reveals Association between Swine Trade and the Spread of Porcine Epidemic Diarrhea Virus in China and across the World](https://academic.oup.com/mbe/article/39/2/msab364/6482749).  
The vector dataset, 'China_map.geojson', can be generated via this link: http://datav.aliyun.com/portal/school/atlas/area_selector.  
Use the command below to execute the 'regions.py' script with 5 required arguments:  
--data: Specify the environmental tabular data you want to visualise (.csv, comma-delimited).  
--locationColumn: In the CSV file, find the column that stores the location information.  
  In the 'Environmental_variables.csv' file, this is the "location" column.  
--map: Specify the input boundary map in GeoJSON format (.geojson).  
--locationVariable: In the GeoJSON input map, find a property that represents the location variable.  
  In the 'China_map.geojson' file, each location is stored in a "name" variable (as part of the "properties").  
--output: Give a name to the output environmental data layer (.geojson).  
You should be able to get an output file of the environmental data layer, named 'Environmental_data_layer.geojson' and used in step 3.
```
regions --data Environmental_variables.csv --locationColumn location --map China_map.geojson --locationVariable name --output Environmental_data_layer.geojson
```




https://github.com/GuyBaele/SpreadGL/assets/1092968/b643e829-89e0-4b0c-8e74-c749913d7749





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
reprojection --input B.1.1.7_England.single.tree.output.csv --lat start_lat,end_lat --lon start_lon,end_lon --source 27700 --target 4326 --output B.1.1.7_England.single.tree.output.reprojected.csv
```

3. Remove geographic outliers.  
If you visualise the reprojected output file created in step 3, there will be many points that fall outside Endland. These outliers were caused by missing geographic data. To identify them, it becomes necessary to refer to a dataset file 'TreeTime_270221.csv', which is an analysis result from the original study (Kraemer et al.). This file contains the location information of each point, i.e. "UTLA" (Upper Tier Local Authorities in England). You will need to check if this value is empty or not. If it is "NULL", that point will fall outside of England. Therefore, the corresponding row (branch) has to be removed.  
Use the following command to execute the 'trimming.py' script with 6 required arguments: input csv file, foreign key field name of input, reference csv file, foreign field name of reference, queried field(s) of reference (comma separator in between, if needed), and output csv file. When this step is done, there will be a new file called 'B.1.1.7_England.single.tree.output.reprojected.cleaned.csv'.
```
trimming --referencing B.1.1.7_England.single.tree.output.reprojected.csv --foreignkey end_lat_original --referenced TreeTime_270221.csv --primarykey endLat --null startUTLA,endUTLA --output B.1.1.7_England.single.tree.output.reprojected.cleaned.csv
```

4. Visualise the spatial layers in spread.gl.  
Follow the previous steps to get different visuals of the spatial layers (see Section 'Visualising a (phylo)geographical spread layer in spread.gl').


https://github.com/GuyBaele/SpreadGL/assets/1092968/31b6076a-4ce4-4b4f-96f2-05210c6f7aeb




### Yellow fever virus (YFV) in Brazil
1. Process the MCC tree file using the command below. This step works in the same way as the RABV example.  
As the tree annotations include the information about regions of highest posterior density (HPD), the relevant data will be saved in the output GeoJSON file automatically.
```
spread --tree YFV.MCC.tree --time 2019-04-16 --location location1,location2
```

2. Crop raster environmental data using a mask map.  
As the environmental data of this example are too large to be hosted on GitHub, you need to **download** historical monthly weather data (maximum temperature, 2010-2019, 2.5 minutes) from:
https://www.worldclim.org/data/monthlywth.html. Only keep the raster files from April 2015 to April 2019 and then save them in a folder called 'wc2.1_2.5m_tmax_2015-2019'. You can find a GeoJSON boundary map in the 'inputdata' folder. This kind of boundary map can also be accessed via: https://www.geoboundaries.org/index.html#getdata.  
Use the command below to execute the 'raster.py' script with 5 required arguments:  
--data: Enter the folder that contains raster data files (.tif).  
--map: Specify the input boundary map (.geojson).   
--locationVariable: In the GeoJSON input map, find a property that represents the location variable.  
  In the 'geoBoundaries-BRA-ADM1.geojson' file, each location/state is stored in a "shapeName" variable (as part of the "properties").  
--locationList: Provide a location list of interest (.txt, comma-delimited).  
--output: Give a name to the output environmental data layer (.csv).  
The average maximum temperatures for all months during the virus outbreak will be calculated automatically. To visualise specific Brazilian provinces instead of the entire world, the raster temperature data will be clipped using a mask made from a GeoJSON boundary map and a list of locations. Finally, a CSV file named 'brazil_region_maxtemp.csv' should be created to serve as the environmental data layer.
```
raster --data wc2.1_2.5m_tmax_2015-2019 --map geoBoundaries-BRA-ADM1.geojson --locationVariable shapeName --locationList Involved_brazilian_states.txt --output brazil_region_maxtemp.csv
```

3. Follow the previous steps to get different visuals of the spatial and environmental layers. For the spatial layer, you can generate a contour layer. For the environmental layer, you will need to choose 'Point' instead of 'Polygon' as the basic layer type. See Sections 'Visualising a (phylo)geographical spread layer in spread.gl' & 'Visualising an environmental data layer in spread.gl' for more information.


https://github.com/GuyBaele/SpreadGL/assets/1092968/bfd2911f-e3a1-41c4-b8b2-2728b9d2ca0b




