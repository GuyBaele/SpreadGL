In this directory, you can find all the scripts that will be used to process maximum clade credibility (MCC) trees, typically from the BEAST v1.10 (or older) software package. Please check below for descriptions of how they work and some command-line based tutorials on how to use different tools. For instance, in spatial_layer_generator, the **spatial.py** script is the key method to call upon, and will delegate further processing tasks to the other scripts. We show how to use these scripts in the different examples on the main page of this GitHub repository.


# Script descriptions

**setup.py** ...

**requirements.txt** lists all the required Python dependencies for the spread.gl processing scripts.

## spatial_layer_generator

**spatial.py** parses the arguments from the client end and automatically passes the values of different parameters on to the corresponding script, depending on the (automatically) detected type of phylogeographic analysis (i.e., discrete or continuous).

**continuous_space_processor.py** accepts values from main.py, parses the tree by calling the code in tree_parser.py, starts a process by continuous_tree_handler.py and returns the result in the format of either csv or geojson.

**continuous_tree_handler.py** deals with a tree file with annotated geographic coordinates in the context of continuous phylogeographic analysis. As the first step, the method of find_clades, provided by the Bio.Phylo package, will be called to traverse the tree and gather the existing information from each node/tip using a depth-first (pre-order) search algorithm. The time information of tips can be obtained from the sequence name (if the information is available there) by using the time_conversion.py script. For each node / tip pf an MCC tree, the location information in the annotation will be extracted using the coordinate_conversion.py script. In the case of processing a BEAST single tree, an output file of geoinfo_generator.r will be used as an additional input parameter.

**discrete_space_processor.py** accepts values from main.py, parses the tree in tree_parser.py, starts a process by discrete_tree_handler.py and returns the result in the format of either csv or geojson.

**discrete_tree_handler.py** works similarly as continuous_tree_handler.py, but the users have to provide an extra location list (with geographic coordinates for the discrete locations) in the context of discrete phylogeographic analysis.

**time_conversion.py** is used to perform conversions between different time formats.

## environmental_layer_generator

**environmental.py** ...

## projection_transformation

**reprojection.py** ...

## outlier_detection

**trimming.py** ...


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
