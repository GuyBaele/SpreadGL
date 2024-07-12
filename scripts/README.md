In this directory, you can find all the scripts that will be used to process maximum clade credibility (MCC) trees, typically from the BEAST v1.10 (or older) software package. Please check below for descriptions of how they work and some command-line based tutorials on how to use different tools. For instance, in spatial_layer_generator, the **spread.py** script is the key method to call upon, and will delegate further processing tasks to the other scripts. We show how to use these scripts in the different examples on the main page of this GitHub repository.


# Script descriptions

**setup.py** describes moudle contents and distribution. It is used for installation.

**requirements.txt** lists all the required Python dependencies (a list of used third-party packages) for the Spread.gl processing scripts.

## spatial_layer_generator

**spread.py** parses the arguments from the client end and automatically passes the values of different parameters onto the corresponding script, depending on the (automatically) detected type of phylogeographic analysis (i.e., discrete or continuous).

**continuous_space_processor.py** accepts values from **spread.py**, processes the tree by calling the code in **continuous_tree_handler.py** and returns the result in the format of either CSV or GeoJSON. By default, the format of the output file is set as GeoJSON, which is a format for encoding a variety of geographic data structures. If the users would like to inspect the result in a table, an output file of the CSV format will be provided by using an additional argument for output.

**continuous_tree_handler.py** deals with a tree file with annotated geographic coordinates in the context of continuous phylogeographic analysis. Some methods from the DendroPy 4.5.2 library will be called to pre-order traverse the tree using the algorithm of depth-first search (DFS). From each tree branch and its two ends, some existing information will be collected, such as length, height, and location information. The time information of tip/external branches will be calculated based on the provided most recent tip time, or obtained from the sequence names (if the information is available there). The time information of node/internal branches will be calculated by **branch_processor.py**. To accommodate potential geographic uncertainty by the 80% HPD (highest posterior density), i.e. the shortest interval that contains 80% of the sampled values, we use GeoJSON polygons for the representation of contours. Each branch information as well as its polygons (if existing) will be put into a spatially bounded entity, called Feature. All the feature objects made from the tree will be stored in a FeatureCollection.

**discrete_space_processor.py** accepts values from **spread.py**, processes the tree by calling the code in **discrete_tree_handler.py** and returns the result in the format of either CSV or GeoJSON. By default, the format of the output file is set as GeoJSON, which is a format for encoding a variety of geographic data structures. If the users would like to inspect the result in a table, an output file of the CSV format will be provided by using an additional argument for output.

**discrete_tree_handler.py** works similarly to **continuous_tree_handler.py**, but the users have to provide an extra location list (with geographic coordinates for the discrete locations) in the context of discrete phylogeographic analysis.

**branch_processor.py** calculates the time information of all the node/internal tree branches iteratively. For each branch, the current end time equals the start time of its child branch, whereas the current start time can be inferred according to its length.

**time_conversion.py** converts time information between different formats.

## bayes_factor_test
**rates.py** performs a Bayes factor test of significant diffusion rates on the BEAST log of discrete phylogeographic inference.

## environmental_layer_generator

**regions.py** creates an environmental layer by adding table data to a GeoJSON map.

**raster.py** creates an environmental layer using raster data along with a location list and a GeoJSON boundary map.

## projection_transformation

**reprojection.py** converts geographic data between different coordinate reference systems.

## outlier_detection

**trimming.py** detects outliers of the current referencing dataset by performing NULL queries on the specified fields of another referenced dataset. As for the example of SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England, it filters out all the branches lacking UTLA (Upper Tier Local Authorities in England) information.


# Tutorials

```
spread --help
```
```
Welcome to the spatial layer generator! You can create a spatial layer for a phylogenetic tree to display in Spread.gl.

optional arguments:
  -h, --help            show this help message and exit
  --tree TREE, -tr TREE
                        Specify the filename (with extension) of your input tree file.
  --time TIME, -ti TIME
                        Enter the date of the most recent tip. It can be either a formatted date or a decimal year.
  --format {YYYY-MM-DD,DD-MM-YYYY}, -f {YYYY-MM-DD,DD-MM-YYYY}
                        This OPTIONAL argument specifies the date format found at the end of phylogenetic tree taxa names. The
                        default format is "YYYY-MM-DD". It also supports "DD-MM-YYYY".
  --location LOCATION, -lo LOCATION
                        Type in the annotation that stores the location information (names or coordinates). If there are two
                        annotations to store coordinates, enter them in the order of latitude and longitude with a comma
                        separator.
  --list LIST, -li LIST
                        Only compulsory for discrete space analysis. Use a location list with its filename extension as an input.
                        This file should be in the csv format with a comma (",") separator, and comprised of three columns with a
                        specific header of "location,latitude,longitude".
  --extension {geojson,csv}, -e {geojson,csv}
                        This OPTIONAL argument specifies the output file extension. The default extension is "geojson". It also
                        supports "csv" to generate a table (without HPD polygons in case of continuous phylogeographic diffusion).
```

```
rates --help
```
```
You can use this tool to perform the Bayes factor test of significant diffusion rates on the BEAST log of discrete phylogeographic inference.

optional arguments:
  -h, --help            show this help message and exit
  --log LOG, -lg LOG    Specify the input BEAST log file (.log).
  --location LOCATION, -lo LOCATION
                        Type in the annotation that stores the location names in the MCC tree, e.g. "region".
  --burnin BURNIN, -b BURNIN
                        Specify burn-in to set how many initial sampled values should be discarded from the analysis. It should be smaller than
                        1 but not less than 0, e.g. "0.1" should be sufficient for most analyses. You can also specify it by using the number
                        of rows, which should be a valid integer in this case.
  --list LIST, -li LIST
                        Use the same location list from your discrete analysis as an input (.csv).
  --layer LAYER, -la LAYER
                        Optional: You can add the Bayes factors to the spatial layer. Use the file of a discrete spatial layer as an input (.csv).
```

```
regions --help
```
```
You can use this tool to create an environmental layer with tabular data.

optional arguments:
  -h, --help            show this help message and exit
  --data DATA, -d DATA  Specify the environmental tabular data you want to visualise (.csv, comma-delimited).
  --locationColumn LOCATIONCOLUMN, -lc LOCATIONCOLUMN
                        In the CSV file, find the column that stores the location information.
  --map MAP, -m MAP     Specify the input boundary map in GeoJSON format (.geojson).
  --locationVariable LOCATIONVARIABLE, -lv LOCATIONVARIABLE
                        In the GeoJSON input map, find a property that represents the location variable.
  --output OUTPUT, -o OUTPUT
                        Give a name to the output environmental data layer (.geojson).
```

```
raster --help
```
```
You can use this tool to create an environmental layer with raster data.

optional arguments:
  -h, --help            show this help message and exit
  --data DATA, -d DATA  Enter the folder that contains raster data files (.tif).
  --map MAP, -m MAP     Specify the input boundary map (.geojson).
  --locationVariable LOCATIONVARIABLE, -lv LOCATIONVARIABLE
                        In the GeoJSON input map, find a property that represents the location variable.
  --locationList LOCATIONLIST, -ll LOCATIONLIST
                        Provide a location list of interest (.txt, comma-delimited).
  --output OUTPUT, -o OUTPUT
                        Give a name to the output environmental data layer (.csv).
```

```
reprojection --help
```
```
Use this tool to convert geographic data between different CRS.

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        Specify the comma-delimited input file with filename extension (.csv).
  --lat LAT, -la LAT    Type in the field names of source latitudes with a comma separator.
  --lon LON, -lo LON    Type in the field names of source longitudes with a comma separator.
  --source SOURCE, -s SOURCE
                        Type in EPSG code of source CRS, e.g. 27700.
  --target TARGET, -t TARGET
                        Type in EPSG code of target CRS. e.g. 4326.
  --output OUTPUT, -o OUTPUT
                        Create a name with filename extension (.csv) for the output file.
```

```
trimming --help
```
```
Use this tool to remove outliers of the current dataset by referring to another one.

optional arguments:
  -h, --help            show this help message and exit
  --referencing REFERENCING, -ri REFERENCING
                        Enter the name of a comma-delimited referencing table with filename extension (.csv).
  --foreignkey FOREIGNKEY, -fk FOREIGNKEY
                        Enter the foreign key field name of the referencing table, e.g. "end_lat".
  --referenced REFERENCED, -rd REFERENCED
                        Enter the name of a comma-delimited referenced dataset with filename extension (.csv).
  --primarykey PRIMARYKEY, -pk PRIMARYKEY
                        Enter the primary key field name of the referenced dataset, e.g. "endLat".
  --null NULL, -n NULL  Specify the queried field(s) in the referenced dataset where NULL values are recorded. If multiple fields are involved
                        in the NULL queries, use a comma separator in between.
  --output OUTPUT, -o OUTPUT
                        Create a name with filename extension (.csv) for the output file.
```
