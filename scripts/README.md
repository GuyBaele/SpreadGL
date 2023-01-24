In this directory, you can find all the scripts that will be used to process maximum clade credibility (MCC) trees, typically from the BEAST v1.10 (or older) software package. Please check below for descriptions of how they work and a command-line based tutorial on how to use them. In short, the **main.py** script is the key method to call upon, and will delegate further processing tasks to the other scripts. We show how to use these scripts in the different examples on the main page of this GitHub repository.

# Script descriptions

**requirements.txt** lists all the required Python dependencies for the spread.gl processing scripts.

**main.py** parses the arguments from the client end and automatically passes the values of different parameters on to the corresponding script, depending on the (automatically) detected type of phylogeographic analysis (i.e., discrete or continuous).

**continuous_space_processor.py** accepts values from main.py, parses the tree by calling the code in tree_parser.py, starts a process by continuous_tree_handler.py and returns the result in the format of either csv or geojson.

**discrete_space_processor.py** accepts values from main.py, parses the tree in tree_parser.py, starts a process by discrete_tree_handler.py and returns the result in the format of either csv or geojson.

**tree_parser.py** parses the MCC tree using two third-party modules: TreeSwift & Bio.Phylo.

**continuous_tree_handler.py** deals with a tree file with annotated geographic coordinates in the context of continuous phylogeographic analysis. As the first step, the method of find_clades, provided by the Bio.Phylo package, will be called to traverse the tree and gather the existing information from each node/tip using a depth-first (pre-order) search algorithm. The time information of tips can be obtained from the sequence name (if the information is available there) by using the time_conversion.py script. For each node / tip pf an MCC tree, the location information in the annotation will be extracted using the coordinate_conversion.py script. In the case of processing a BEAST single tree, an output file of geoinfo_generator.r will be used as an additional input parameter.

**geoinfo_generator.r** extracts geographic information in the annotation of a BEAST single tree using a third-party R package: treeio.

**tree_processor.py** was mainly designed to infer the dates of each node by recursively traversing the MCC tree.

**time_conversion.py** is used to perform conversions between different time formats.

**coordinate_conversion.py** is used to parse coordinates in the tree annotation or from the location list.

**pattern_management.py** contains different regular expressions that can match dates, floating point numbers, coordinates or strings.

**discrete_tree_handler.py** works similarly as continuous_tree_handler.py, but the users have to provide an extra location list (with geographic coordinates for the discrete locations) in the context of discrete phylogeographic analysis.

**geojson_file_generator.py** generates geographic data structures for each branch in the MCC tree. By default, the format of output file is set as GeoJSON, which is a format for encoding a variety of geographic data structures. Feature and FeatureCollection are two types of objects within the GeoJSON format. A FeatureCollection contains an array of Feature objects. A Feature object represents a spatially bounded entity and contains several members, such as "geometry" and "properties". The value of the properties member can be any JSON object. As the tree information is recorded via its branches, each branch can serve as the properties member of a Feature object. For continuous phylogeographic analysis, we may need to accommodate uncertainty using the 80% HPD (highest posterior density), which is the shortest interval that contains 80% of the sampled values. On the map, this uncertainty can be visualised as contours or polygons.

<details><summary>Click here to see an example of a FeatureCollection with two Feature objects.</summary>

```
{
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    []
                ]
            },
            "properties": {
                "id":17,
                "duration":0.6207730480719,
                "name":"MH018115|Brazil|ES|VendaNovaDoImigrante|NP|NA|IAL-11_11|2017-01-24",
                "start_time":"2016-06-11 08:40:29",
                "end_time":"2017-01-24 11:59:59",
                "start_latitude":-20.51398598643596,
                "start_longitude":-46.85916960400302,
                "end_latitude":-20.433141927814653,
                "end_longitude":-41.067196968419054
            }
        },
        {"type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-48.428766,-21.350363],[-48.606715,-21.256626],[-48.69569,-21.101844],[-48.501579,-21.019836],
                        [-48.339791,-20.870381],[-47.734757,-20.839631],[-47.539018,-20.92914],[-47.472875,-21.139962],
                        [-47.571243,-21.320161],[-47.805942,-21.437464],[-48.072867,-21.44995],[-48.428766,-21.350363]
                    ]
                ]
            },
            "properties": {
                "id":18,
                "duration":0.2150216520605,
                "name":"None",
                "start_time":"2015-11-30 09:37:52",
                "end_time":"2016-02-17 00:18:13",
                "start_latitude":-20.768129100821106,
                "start_longitude":-47.33880273745724,
                "end_latitude":-21.127361903797887,
                "end_longitude":-47.98910670165459
            }
        }
    ]
}
```

</details>

# Tutorial

If you type "python3 main.py --help" in a terminal in this folder, you should be able to see the following help messages.
```
Welcome to this processing tool! You can convert a single phylogenetic tree to an acceptable input file for Spread.gl.

optional arguments:
  -h, --help            show this help message and exit
  --tree TREE, -t TREE  Specify the file name of your phylogenetic tree with filename extension.
  --date {float,datetime}, -d {float,datetime}
                        At the end of sequence names, you can typically find the date format. If it is a floating-point number, enter "float". If it is ISO-8601
                        (Year-Month-Day/yyyy-mm-dd), enter "datetime". When it is incomplete, the first day of the corresponding month or year will be used.
  --location LOCATION, -l LOCATION
                        Optional, only mandatory when processing MCC tree files. Enter the two annotations, storing latitudes and longitudes (in this order), with
                        a comma separator. If there is only one annotation that stores the location names, enter this annotation without a comma.
  --geoinfo GEOINFO, -g GEOINFO
                        Optional, only mandatory when processing BEAST single tree files. Specify the name of the file containing extra geographic information
                        with filename extension. This file should be generated by R script before this step.
  --list LIST, -li LIST
                        Optional, only mandatory in the case of discrete space. Specify the file name of your list of coordinates with filename extension. This
                        file should be in the csv format with a comma (",") separator, and should be comprised of three columns with a specific header of
                        "location,latitude,longitude".
  --format {csv}, -f {csv}
                        Optional: Type in "csv" if you would like to inspect your output file in a tabular format.
```
