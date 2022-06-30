# SpreadGL
Main development repository for SpreadGL
# Dataset Examples
In the "data examples" folder, You can find some dataset examples for visualization.
# User Guide
1. Clone Repository\
"git clone git@github.com:FlorentLee/visualization_demo.git"

3. Install\
"cd visualization_demo"
"npm install"

4. Mapbox Token\
As Kepler.gl is built on top of Mapbox, you need to get a mapbox account and an access token at mapbox.com.\
My own access token was already embedded in App.js. Feel free to replace it.

5. Start\
"npm start"

6. Load Data\
Drag and drop a .csv file into the application.

7. Add Layer\
Select Basic - Point and select latitude + longitude columns.

8. Add Filter\
Go to the Filters panel, add a filter and select the collection time column.

9. Set visualisation settings\
Select increcremental time window, set its width and press play to start the animation.
