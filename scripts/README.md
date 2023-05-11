In this directory, you can find all the scripts that will be used to process maximum clade credibility (MCC) trees, typically from the BEAST v1.10 (or older) software package. Please check below for descriptions of how they work and some command-line based tutorials on how to use different tools. For instance, in spatial_layer_generator, the **spatial.py** script is the key method to call upon, and will delegate further processing tasks to the other scripts. We show how to use these scripts in the different examples on the main page of this GitHub repository.


# Script descriptions

**setup.py** describes moudle contents and distribution. It is used for installation.

**requirements.txt** lists all the required Python dependencies for the Spread.gl processing scripts.

## spatial_layer_generator

**spatial.py** parses the arguments from the client end and automatically passes the values of different parameters on to the corresponding script, depending on the (automatically) detected type of phylogeographic analysis (i.e., discrete or continuous).

**continuous_space_processor.py** accepts values from spatial.py, processes the tree by calling the code in continuous_tree_handler.py and returns the result in the format of either csv or geojson. By default, the format of output file is set as GeoJSON, which is a format for encoding a variety of geographic data structures. If the users would like to inspect the result in the table, an output file of the CSV format will be provided by using an additional argument for output.

**continuous_tree_handler.py** deals with a tree file with annotated geographic coordinates in the context of continuous phylogeographic analysis. Some methods from the baltic 0.1.6 library will be called to traverse the tree and gather the existing information (time & location) from each node/tip using a depth-first search algorithm. The time information of tips can be obtained from the sequence name (if the information is available there) and then formated by using time_conversion.py script. To accommodate potentially geographic uncertainty by the 80% HPD (highest posterior density), i.e. the shortest interval that contains 80% of the sampled values, we use GeoJSON polygons for representation of contours. Each branch information as well as its polygons (if existing) will be put into a spatially bounded entity, called Feature. All the feature objects made from the tree will be stored in a FeatureCollection.

**discrete_space_processor.py** accepts values from spatial.py, processes the tree by calling the code in discrete_tree_handler.py and returns the result in the format of either csv or geojson.

**discrete_tree_handler.py** works similarly as continuous_tree_handler.py, but the users have to provide an extra location list (with geographic coordinates for the discrete locations) in the context of discrete phylogeographic analysis.

**branch_processor.py** calculates the time of the parent tree branches.

**time_conversion.py** converts time from decimal years to datetime.

## bayes_factor_test
**rates.py** performs Bayes factor test of significant diffusion rates on the BEAST log of discrete phylogeographic inference.

## environmental_layer_generator

**regions.py** creates the environmental layer using tabular data.

**raster.py** creates the environmental layer using raster data.

## projection_transformation

**reprojection.py** converts geographic data between different coordinate reference systems.

## outlier_detection

**trimming.py** detects outliers of the current dataset by performing NULL queries on the specified fields of another referenced dataset. As for the example of SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England, it filters out all the branches in lack of information about UTLA (English Upper Tier Local Authorities).


# Tutorials

```
spread --help
```
```
Welcome to the spatial layer generator! You can create a spatial layer for a phylogenetic tree to display in Spread.gl.

optional arguments:
  -h, --help            show this help message and exit
  --tree TREE, -tr TREE
                        Specify the name of your input tree file with filename extension.
  --time TIME, -ti TIME
                        Enter the date of the most recent tip. It can be either in the format of YYYY-MM-DD or decimal year.
  --location LOCATION, -lo LOCATION
                        Type in the annotation that stores the location information (names or coordinates). If there are two annotations to store coordinates,
                        enter them in the order of latitude and longitude with a comma separator.
  --list LIST, -li LIST
                        Only compulsory for discrete space analysis. Use a location list with its filename extension as an input. This file should be in the
                        csv format with a comma (",") separator, and comprised of three columns with a specific header of "location,latitude,longitude".
  --format {csv}, -f {csv}
                        It is optional. If you want to check the output in a table, use "csv" in this argument.
```

```
rates --help
```
```
You can use this tool to perform Bayes factor test of significant diffusion rates on the BEAST log of discrete phylogeographic inference.

optional arguments:
  -h, --help            show this help message and exit
  --log LOG, -lg LOG    Specify the input BEAST log file (.log).
  --location LOCATION, -lo LOCATION
                        Type in the annotation that stores the location names in the MCC tree, e.g. "region".
  --burnin BURNIN, -b BURNIN
                        Specify burn-in to set how many initial samped values should be discarded from the analysis. It should be smaller than
                        1 but not less than 0, e.g. "0.1" should be sufficient for most analysis. You can also specify it by using the number
                        of rows, which should be a valid integer in this case.
  --list LIST, -li LIST
                        Use the same location list from your discrete analysis as an input (.csv).
  --layer LAYER, -la LAYER
                        Optional: You can add the Bayes factors to the spatial layer. Use the file of discrete spatial layer as an input (.csv).
```

```
regions --help
```
```
You can use this tool to create environmental layers using tabular data.

optional arguments:
  -h, --help            show this help message and exit
  --map MAP, -m MAP     Specify the input boundary map in GeoJSON format (.geojson).
  --locationVariable LOCATIONVARIABLE, -lv LOCATIONVARIABLE
                        In the GeoJSON input file, find the property that represents the location variable.
  --data DATA, -d DATA  Specify the environmental data you want to visualise in an environmental layer (.csv, comma-delimited).
  --locationColumn LOCATIONCOLUMN, -lc LOCATIONCOLUMN
                        In the CSV file, find the column that holds the location information.
  --output OUTPUT, -o OUTPUT
                        Give a file name in which to store the output environmental layer (.geojson).
```

```
raster --help
```
```
You can use this tool to create environmental layers using raster data.

optional arguments:
  -h, --help            show this help message and exit
  --data DATA, -d DATA  Enter the folder that contains raster data files (.tif).
  --map MAP             Specify the input boundary map (.geojson).
  --mask MASK           Use a list of locations / location IDs of interest as a mask (.txt, comma-delimited).
  --foreignkey FOREIGNKEY, -f FOREIGNKEY
                        Find a foreign key variable in the map that refers to the mask.
  --output OUTPUT, -o OUTPUT
                        Give a name to the output environmental layer (.csv).
```

```
reprojection --help
```
```
You can use this tool to convert geographic data between different CRS.

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        Specify the comma-delimited input file with filename extension (.csv).
  --lat LAT, -la LAT    Type in the field names of source latitudes with a comma separator.
  --lng LNG, -ln LNG    Type in the field names of source longitudes with a comma separator.
  --src SRC, -s SRC     Type in EPSG code of source CRS, e.g. 27700.
  --trg TRG, -t TRG     Type in EPSG code of target CRS. e.g. 4326.
  --output OUTPUT, -o OUTPUT
                        Create a name with filename extension (.csv) for the output file.
```

```
trimming --help
```
```
You can use this tool to remove outliers of the current dataset by referring to another one.

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        Specify the comma-delimited input file with filename extension (.csv).
  --key KEY, -k KEY     Enter the foreign key field name of the input dataset. In the case of geographic outliers, it can be the latitude field of ending
                        points.
  --refer REFER, -r REFER
                        Specify the comma-delimited reference dataset with filename extension (.csv).
  --foreign FOREIGN, -f FOREIGN
                        Enter the foreign field name of the referenced dataset. In the case of geographic outliers, it can be the latitude field of ending
                        points.
  --null NULL, -n NULL  Enter the queried field(s) of the referenced dataset, where NULL values will be recorded. If there are multiple fields to be used in
                        the NULL queries, use a comma separator in between.
  --output OUTPUT, -o OUTPUT
                        Create a name with filename extension (.csv) for the output file.
```
