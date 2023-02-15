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

**time_conversion.py** converts time from decimal years to datetime.

## environmental_layer_generator

**environmental.py** creates environmental layers by adding data to GeoJSON maps.

## projection_transformation

**reprojection.py** converts geographic data between different coordinate reference systems.

## outlier_detection

**trimming.py** detects outliers of the current dataset by performing NULL queries on the specified fields of another referenced dataset. As for the example of SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England, it filters out all the branches in lack of information about UTLA (English Upper Tier Local Authorities).


# Tutorials

```
spatial --help
```
```
Welcome to the spatial layer generator! You can create a spatial layer for a phylogenetic tree to display in Spread.gl.

optional arguments:
  -h, --help            show this help message and exit
  --tree TREE, -t TREE  Specify the file name of your phylogenetic tree with filename extension.
  --location LOCATION, -l LOCATION
                        Type in the annotation that stores the location information or coordinates. Or type in the two annotations storing latitude and longitude
                        (in this order) with a comma separator.
  --list LIST, -li LIST
                        Optional, only mandatory in the case of discrete space. Specify the file name of your list of coordinates with filename extension. This
                        file should be in the csv format with a comma (",") separator, and should be comprised of three columns with a specific header of
                        "location,latitude,longitude".
  --format {csv}, -f {csv}
                        Optional: Type in "csv" if you would like to inspect your output file in a tabular format.
```

```
environmental --help
```
```
Welcome to the environmental layer generator! You can create the environmental layers with environmental data to display in Spread.gl.

optional arguments:
  -h, --help            show this help message and exit
  --region REGION, -r REGION
                        Specify the GeoJSON file with filename extension as the region part of the environmental layer.
  --key KEY, -k KEY     Enter the foreign key field of the GeoJSON file. In this case, it can be "name" in the properties.
  --data DATA, -d DATA  Specify the comma-delimited CSV file with filename extension as the data part of the environmental layer.
  --foreign FOREIGN, -f FOREIGN
                        Enter the foreign/referenced field of the CSV file. In this case, it can be the "location" column.
  --output OUTPUT, -o OUTPUT
                        Create a name with filename extension (.geojson) for the output file.
```

```
reprojection --help
```
```
Welcome to this tool for projection transformation! You can convert geographic data between different CRS.

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
Welcome to this tool for outlier detection! You can remove outliers of the current dataset by referring to another one.

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        Specify the comma-delimited input file with filename extension (.csv).
  --key KEY, -k KEY     Enter the foreign key field name of the input dataset. In the case of geographic outliers, it can be the latitude
                        field of ending points.
  --refer REFER, -r REFER
                        Specify the comma-delimited reference dataset with filename extension (.csv).
  --foreign FOREIGN, -f FOREIGN
                        Enter the foreign field name of the referenced dataset. In the case of geographic outliers, it can be the latitude
                        field of ending points.
  --null NULL, -n NULL  Enter the queried field(s) of the referenced dataset, where NULL values will be recorded. If there are multiple fields
                        to be used in the NULL queries, use a comma separator in between.
  --output OUTPUT, -o OUTPUT
                        Create a name with filename extension (.csv) for the output file.
```
