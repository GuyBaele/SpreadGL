# SpreadGL
Main development repository for SpreadGL.

# Installation
1. Clone Rsepository\
"git clone git@github.com:FlorentLee/SpreadGL.git"

2. Install Packages\
"npm install"
"npm audit fix --force"

3. Mapbox Token\
As Kepler.gl is built on top of Mapbox, you need to get a mapbox account and an access token at mapbox.com.\
My own access token was already embedded in App.js. Feel free to replace it.

4. Start\
"npm start"

# Examples
In the "data examples" folder, you can find some dataset examples for visualization.

# Point Layer Visualization
1. Load Data\
Drag and drop "Belgium Omicron Cases.csv" into the application. (Belgium Omicron Cases)

2. Add Layers\
In the Layers panel, add a new layer.\
Select Point as the layer type, Latitude and Longitude as the columns.

3. Add Filters\
Go to the Filters panel, add a new filter.\
Select the Collection Time as the column.

4. Set Visualisation\
FInd the incremental time window, set its width and click the play button to start the animation.

# Arc Layer Visualisation:
1. Load Data\
Drag and drop .csv into the application.

2. Add Layer\
In the Layers panel, add a new layer.\
Select Arc as the layer type, the fields below as the columns.\
Source Lat: pickup_latitude\
Source Lng: pickup_longitude\
Target Lat: dropoff_latitude\
Target Lng: dropoff_longitude

3. Add Filter\
Go to the Filters panel, add a new filter\
Select tpep_pickup_datetime / tpep_dropoff_datetime as the column.

4. Set visualisation settings\
FInd the incremental time window, set its width and click the play button to start the animation.

