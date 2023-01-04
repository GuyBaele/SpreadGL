In this directory, you can find all the scripts that will be used to process maximum clade credibility (MCC) trees, typically from the BEAST v1.10 (or older) software package. Please check below for descriptions of how they work and a command-line based tutorial on how to use them. In short, the **main.py** script is the key method to call upon, and will delegate further processing tasks to the other scripts. We show how to use these scripts in the different examples on the main page of this GitHub repository.

# Script descriptions

**main.py** parses the arguments from the client end and passes the values of different parameters to the corresponding script with the correct type of phylogeographic analysis.

**continuousProcessor.py:** An interface accepts values from main.py, parses the tree in TreeParser.py, starts the process with continuousMCCTreeParser.py and returns the result in the format of either csv or geojson.

**discreteProcessor.py:** An interface accepts values from main.py, parses the tree in TreeParser.py, starts the process with discreteMCCTreeParser.py and returns the result in the format of either csv or geojson.

**TreeParser.py** will parse the MCC tree using the third-party modules TreeSwift & Biopython.

**continuousMCCTreeParser.py** extracts information from MCC trees with annotated geographic coordinates in the context of continuous phylogeographic analysis. As the first step is to process details from the summary MCC tree, it extracts time information via TimeConversion.py as well as the location information via CoordinateConversion.py. Afterwards, it calls the function of iterateTree in BranchInference.py to traverse the whole tree and replace the empty values in each tree branch with correct information. Finally, the result will be stored in a dictionary/hash map.

**BranchInference.py** implements a depth first search algorithm to traverse the entire MCC tree in order to obtain existing information from each branch and then store it in a stack. In the meantime, missing values will be replaced by calling the function of branchProcessor. To be more specific, here we use the start & end point to represent the two ends of one tree branch. The location information of the current start point is the same as that of the previous end point, where the latter is known. The time information of the current end point can be retrieved from the next start point. We can then calculate the time for the current start point, which also serves as the time for the previous end point. In all, we can gather and infer enough details for each branch via traversal.

**TimeConversion.py** s used to perform conversions between different time formats.

**CoordinateConversion.py** is used to parse coordinates in the tree annotation or from the location list.

**PatternManagement.py** stores different regular expressions that can match dates, floating point numbers, coordinates or strings.

**discreteMCCTreeParser.py** works similarly as continuousMCCTreeParser.py, but the users have to provide an extra location list (with geographic coordinates for the discrete locations) in the context of discrete phylogeographic analysis.

**geojsonLayer.py:** As the type of final output is set as GeoJSON by default, we created feature(s) for each tree branch, using the parsed tree information as the properties part. Then, we put them into a feature collection. Eventually, we exported it as a GeoJSON file. For continuous phylogeographic analysis, we may need to accommodate uncertainty using the 80% HPD (highest posterior density), which is the shortest interval that contains 80% of the sampled values. On the map, it can be reflected as contours surrounding the points. In this case, one or multiple polygons should be created to serve as the geometry part of feature(s).

**requirements.txt:** This file lists all the required dependencies.

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
