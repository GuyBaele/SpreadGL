# Spread.gl - Visualising Pathogen Dispersal in a High-performance Browser Application
Main development repository and webpage for spread.gl, hosting installation files and input data files for several visualisation examples along with short tutorials and example output videos.

# Installation
1. Clone repository
```
git clone git@github.com:GuyBaele/SpreadGL.git
```
2. Install packages
```
cd SpreadGL
npm install
```
3. Sign up for a Mapbox account and create an access token at mapbox.com.  
   Open the 'mapbox.js' file in the src directory to insert your own token, and save the file.
4. Start the project, which will open a browser window
```
npm start
```
In case of any problems running 'npm start', you may have to install the 'assert' and 'url' packages as well
```
npm install assert
npm install url
```

# Processing MCC tree files
1. Copy the scripts folder to the directory which contains the target tree. More information regarding the different scripts can be found in the README of the scripts folder.
2. Install the required python packages in a new terminal in the scripts folder. You only have to do it once.  
   Note: Please make sure that you have already installed Python 3 before this step. 
```
pip install -r requirements.txt
```
3. Check the descriptions of arguments.
```
python3 main.py --help
```
4. Process the MCC tree you want to visualise. For example, for each of the three visualisations shown below, these are the commands required (but see the examples below and the scripts directory for more information).
```
python3 main.py --tree B.1.1.7_England.single.tree --location coordinates --format csv
python3 main.py --tree YFV.MCC.tree --location location1,location2
python3 main.py --tree PEDV_China.MCC.tree --location location --list Capital_Coordinates_Involved_Provinces.csv
```

# Animation examples in spread.gl
In the 'inputdata' folder, you can find all the required input files for our 3 examples in the manuscript.

## SARS-CoV-2 lineage B.1.1.7 (VOC Alpha) in England
Please make sure that you have already installed R before processing.

1.Process the tree file using the following command:
```
python3 main.py --tree B.1.1.7_England.single.tree --location coordinates --format csv
```
This command does the following: Execute the Python script of main.py with 3 arguments, which represents the input filename, the annotation that contains coordinates information, and the table format of output file respectively. When this step is done, a file 'B.1.1.7_England.single.tree.output.csv' will have been created.

2. Reproject coordinates. Due to the original tree file using the British National Grid coordinate reference system (CRS), which is not supported in spread.gl, you need to perform an additional step (using the file 'B.1.1.7_England.single.tree.output.csv' created in step 2) to convert it to another CRS (i.e., the World Geodetic System 1984; WGS84) with the R script 'projection_transformation.r'. Use the following command:
```
Rscript projection_transformation.r B.1.1.7_England.single.tree.output.csv B.1.1.7_England.single.tree.reprojected.output.csv
```
Make sure to enter the input filename as the first argument and the output filename as the second argument. When this step is done, a file 'B.1.1.7_England.single.tree.reprojected.output.csv' will have been created.

3. Remove geographic outliers. If you visualise the reprojected output file that was created in step 3, there will be many points that fall outside Endland. These outliers were caused by missing geographic data. To identify them, it becomes necessary to refer to a dataset file 'TreeTime_270221.csv', which is an analysis result from the original study (Kraemer et al.). This file contains the location information of each point, i.e. UTLA (Upper Tier Local Authorities in England). You will need to check if this value is empty or not. If it is 'NA', that point will fall outside of England. Therefore, the corresponding branch has to be removed. The python script 'outlier_detection.py' deals with this task.
```
python3 outlier_detection.py --help
```
Enter the above command to see the help messages as below.
```
  --input INPUT, -i INPUT
                        Enter the input file name with filename extension.
  --reference REFERENCE, -r REFERENCE
                        Enter the reference dataset name with filename extension.
  --output OUTPUT, -o OUTPUT
                        Enter the output file name with filename extension.
```
Use the following command to execute this script:
```
python3 outlier_detection.py --input B.1.1.7_England.single.tree.reprojected.output.csv --reference TreeTime_270221.csv --output B.1.1.7_England.single.tree.final.output.csv
```
When this step is done, the end result file 'B.1.1.7_England.single.tree.final.output.csv' will have been created.

4. Visualise the end result.
Now, you can load the end result in Spread.gl. Click the buttom "Add Data". Drag & drop the file of 'B.1.1.7_England_final_output.csv' there. You can customise the visualisation by adjusting the parameters in the side panal, i.e. showing / hiding / creating / deleting / reordering / colouring different layers, adding the end_time as a filter to create animation, and applying your favourite map style, etc.

https://user-images.githubusercontent.com/74751786/200294175-24cf3c0a-92c6-49b6-ad9d-ed5dd57fe60d.mp4

## Yellow fever virus in Brazil
1. Process the tree file using the following command:
```
python3 main.py --tree YFV.MCC.tree --location location1,location2
```
This command does the following: Execute the Python script of main.py with 2 arguments, which represents the input filename and the two annotations (with a comma separator) that contain coordinates information. When this step is done, a file 'YFV.MCC.tree.output.geojson' will have been created.

2. Generate the file of 'brazil_region_maxtemp.csv' as a temperature layer. (To Be Continued)

3. Visualise the end result.

https://user-images.githubusercontent.com/74751786/200294883-a1a28d8c-44c0-4a0a-ab89-b3d137e704f1.mp4

## Porcine epidemic diarrhea virus (PEDV) in China
1. Process the tree file using the following command:
```
python3 main.py --tree PEDV_China.MCC.tree --location location --list Capital_Coordinates_Involved_Provinces.csv
```
This command does the following: Execute the Python script of main.py with 3 arguments, which represents the input filename, the annotation that contains location information, and a list of coordinates of involved locations. When this step is done, a file 'YFV.MCC.tree.output.geojson' will have been created.

2. Generate the file of 'Pig_Population_Involved_Provinces.geojson' as an environmental layer. (To Be Continued)

3. Visualise the end result. To add a custom base map style, you need to create a custom map style on Mapbox Studio (https://studio.mapbox.com). An official manual can be found via the following link (https://docs.mapbox.com/studio-manual/guides/). Once completed, open the Base Map panel, click the add map style button to open the custom map style modal, paste in the mapbox style Url. Note that you need to paste in your mapbox access token if your style is not published.

https://user-images.githubusercontent.com/74751786/205175522-5f639239-79d6-48c4-a097-837df9e50fa6.mp4
