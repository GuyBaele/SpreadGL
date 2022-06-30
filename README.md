# SpreadGL
Main development repository for SpreadGL.

# Installation
1. Clone Rsepository\
"git clone git@github.com:FlorentLee/SpreadGL.git"

2. Enter Directory\
"cd ...\SpreadGL"

3. Install Packages\
"npm install"

4. Mapbox Token\
As Kepler.gl is built on top of Mapbox, you need to get a mapbox account and an access token at mapbox.com.\
My own access token was already embedded in App.js. Feel free to replace it.

5. Start\
"npm start"

# Examples
In the "data examples" folder, you can find some dataset examples for visualization.

# Point Map Visualization
1. Load Data\
Drag and drop a CSV file into the application.

2. Add Layers\
In the Layers panel, add a new layer.\
Select Point as the layer type, Latitude and Longitude as the columns.

3. Add Filters\
Go to the Filters panel, add a new filter.\
Select the Collection Time as the column.

4. Set Visualisation\
Select increcremental time window, set its width and click the play button to start the animation.
