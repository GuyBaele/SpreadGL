In this directory, you can find all the scripts that will be used to process maximum clade credibility (MCC) trees, typically from the BEAST v1.10 (or older) software package. Please check below for descriptions of how they work and a command-line based tutorial on how to use them. In short, the **main.py** script is the key method to call upon, and will delegate further processing tasks to the other scripts. We show how to use these scripts in the different examples on the main page of this GitHub repository.

# Script descriptions

**requirements.txt** lists all the required Python dependencies.

**main.py** parses the arguments from the client end and passes the values of different parameters to the corresponding script with the correct type of phylogeographic analysis.

**continuous_space_processor.py:** accepts values from main.py, parses the tree in tree_parser.py, starts a process by continuous_tree_handler.py and returns the result in the format of either csv or geojson.

**discrete_space_processor.py:** accepts values from main.py, parses the tree in tree_parser.py, starts a process by discrete_tree_handler.py and returns the result in the format of either csv or geojson.

**tree_parser.py** parses the MCC tree using two third-party modules: TreeSwift & Bio.Phylo.

**continuous_tree_handler.py** deals with MCC trees with annotated geographic coordinates in the context of continuous phylogeographic analysis. As the first step, the method of find_clades, provided by Bio.Phylo package, will be called to traverse the tree and gather the exsiting information from each node/tip. It implements the depth-first (preorder) search algorithm. For each node / tip, the location information in the annotation can be extracted by coordinate_conversion.py. The time information of tips can also be obtained from the sequence name by time_conversion.py.

In order to better reflect the relationship of parent node and child node, we used starting point & ending point to denote them respectively and put their information (key-value pairs) together in the same dictionary, denoted as branch. Branches will be nested in a list. Then, we processed these branches via tree_processor.py. Eventually, the list of branches (dictionaries) will be returned as a result.

**tree_processor.py** was mainly designed to infer the dates of each node by recursively referring to the date of its child node and their distance (length of branch). As the branches were stored in the way of pre-order traversal, we created a stack and pushed them into it. While the branch at the top of the stack has a tip as its ending point or been visited twice (no more sub-branch in the stack), the method of *exchange_branch_information will be called. The goal is to exchange information and infer the values of date between each branch and its sub-branch.

**exchange_branch_information:* In this method, the current branch at the top of the stack will be poped out. The time of the ending point of its previous branch should be equal to that of the starting point of the current branch. The starting point of the previous branch can hence be calculated by referring to the branch length. As for the location of the starting point of the current branch, it is the same as that of the ending point of its previous branch. Until now, all the information of both branches is completely recorded. The visit times of the previous branch will be added by one.

**time_conversion.py** is used to perform conversions between different time formats.

**coordinate_conversion.py** is used to parse coordinates in the tree annotation or from the location list.

**pattern_management.py** stores different regular expressions that can match dates, floating point numbers, coordinates or strings.

**discrete_tree_handler.py** works similarly as continuous_tree_handler.py, but the users have to provide an extra location list (with geographic coordinates for the discrete locations) in the context of discrete phylogeographic analysis.

**geojson_file_generator.py:** By default, the format of output file is set as GeoJSON. Feature and FeatureCollection are two types of GeoJSON. A FeatureCollection contains an array of Feature Objects. A Feature object represents a spatially bounded entity and contains several members, such as "geometry" and "properties". The value of the properties member can be any JSON object. As the tree information is recorded in many branches (dictionaries), each branch can serve as the properties member of a Feature object. For continuous phylogeographic analysis, we may need to accommodate uncertainty using the 80% HPD (highest posterior density), which is the shortest interval that contains 80% of the sampled values. On the map, it can be reflected as contours surrounding the points. In this case, each ending point of the branches may correspond to one or multiple polygons, which can become the geometry memebr of the Feature object(s). To conclude, we created one or several Feature object(s) for each branch, put all of them into a FeatureCollection and exported a GeoJSON file.

<details><summary>CLICK ME to see an example.</summary>

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

If you type "python3 main.py --help" in a terminal at the current folder, you should be able to see the following text.

    Welcome to this processing tool! You can convert MCC trees to acceptable input files for Kepler.gl.

    optional arguments:
    
    -h, --help             show this help message and exit
  
    --tree TREE, -t TREE   Specify the file name of your MCC tree with filename extension.
  
    --date {decimal,yyyy-mm-dd}, -d {decimal,yyyy-mm-dd}  At the end of sequence names, find the date format. If it is a decimal number, enter "decimal". 
      If it is ISO-8601 (Year-Month-Day), enter "yyyy-mm-dd". When it is incomplete, the first day of the corresponding month or year will be applied.
    
    --location LOCATION, -l LOCATION  Enter the two annotations, storing latitudes and longitudes in this order, with a comma separator.
      If there is only one annotation that stores either coordinates or location names, enter this annotation without comma.
  
    --list LIST, -li LIST  Optional, only mandatory for discrete space: Specify the file name of your list of coordinates with filename extension. This file
      should be in the format of ".csv" with the separator of "," and comprised of three columns with a specific header of "location,latitude,longitude".
  
    --type {csv}, -t {csv} Optional: Type in "csv" if you would like to inspect your output file in a tabular format.
