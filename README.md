# SpreadGL
Main development repository for SpreadGL.

# Dataset Examples
In the "data examples" folder, you can find some dataset examples for visualization.

# User Guide
1. Clone rsepository\
"git clone git@github.com:FlorentLee/SpreadGL.git"

2. Enter this directory\
"cd ...\SpreadGL"

3. Install packages\
"npm install"

4. Mapbox Token\
As Kepler.gl is built on top of Mapbox, you need to get a mapbox account and an access token at mapbox.com.\
My own access token was already embedded in App.js. Feel free to replace it.

5. Start\
"npm start"

6. Load Data\
Drag and drop a CSV file into the application.

7. Add Layer\
In the Layers panel, add a new layer.\
Select Point as the layer type, Latitude and Longitude as the columns.

8. Add Filter\
Go to the Filters panel, add a new filter\
Select the Collection Time as the column.

9. Set visualisation\
Select increcremental time window, set its width and press play to start the animation.
