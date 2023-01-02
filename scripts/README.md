In this directory, you can find each script that will be used to process MCC trees. Please check below for the explanations about how they work and how to use them.

**main.py:** It parses the arguments from the client end and passes the values of different parameters to the corresponding script with the correct type of phylogeographic analysis.

**continuousProcessor.py:** An interface accepts values from main.py, parses the tree in TreeParser.py, starts the process with continuousMCCTreeParser.py and returns the result in the format of either csv or geojson.

**discreteProcessor.py:** An interface accepts values from main.py, parses the tree in TreeParser.py, starts the process with discreteMCCTreeParser.py and returns the result in the format of either csv or geojson.

**TreeParser.py:** The MCC tree will be parsed using the third-party modules, TreeSwift & Biopython.

**continuousMCCTreeParser.py:** This script extracts information from MCC trees with annotated geographic coordinates in the context of continuous phylogeographic analysis. As the first step is to process details in the summary tree, it extracts time information via TimeConversion.py as well as the location information via CoordinateConversion.py. Afterwards, it calls the function of iterateTree in BranchInference.py to traverse the whole tree and replace the empty values in each tree branch with correct information. Finally, the result will be stored in a dictionary/hash map.

**BranchInference.py:** The algorithm of Deep-first Search will be implemented to traverse the whole tree in order to obtain originally existing information from each branch and then store it in a stack. In the meanwhile, missing values will be replaced by calling the function of branchProcessor. To be more specific, here we use the start & end point to represent the two sides of one tree branch. The location information of the start point is the same as that of the previous end point, which is already known. The time information of the end point can be retrieved from the next start point. We can then calculate the time for the start point, which also serves as the time for the previous end point. In all, we can gather and infer enough details for each branch via traversal.

**TimeConversion.py:** It is used to realise conversion functions among different time formats.

**CoordinateConversion.py:** It is used to parse coordinates in the tree annotation or from the location list.

**PatternManagement.py:** This script stores different regular expressions that can match dates, floating point numbers, coordinates or strings.

**discreteMCCTreeParser.py:** It works in the same way as continuousMCCTreeParser.py. But the users have to provide an extra location list in the context of discrete phylogeographic analysis.

**geojsonLayer.py:** As the type of final output is set as GeoJSON by default, we create features for each tree branch, put them into a feature collection and then export it as a GeoJSON file. For continuous phylogeographic analysis, we may need to accommodate uncertainty using the 80% HPD (highest posterior density), which is the shortest interval that contains 80% of the sampled values. On the map, it can be reflected as contours surrounding the points. In this case, we create multiple polygons as the geometry of the features.

**requirements.txt:** This file lists all the required dependencies.
