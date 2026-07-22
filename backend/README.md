# spread.gl Backend Processing Toolkit

This directory contains the Python-based ETL (Extract, Transform, Load) backend processing toolkit for **spread.gl v2.0**. It processes Maximum Clade Credibility (MCC) trees (from BEAST v1.10 or BEAST v2), parses MCMC logs, transforms spatial projections, filters outliers, and generates GeoJSON outputs suitable for 3D visualization.

---

## 📂 Backend Directory Structure & Functioning Scripts

### 1. Root Scripts
* **[main.py](file:///Users/u0150975/Downloads/SpreadGL/backend/main.py)**: The FastAPI server that exposes the endpoints for the frontend. It integrates all ETL processors, handles file uploads, executes processing, runs Bayes Factor analysis, parses Markov jumps, and returns combined GeoJSON datasets.
* **[run_regression_tests.py](file:///Users/u0150975/Downloads/SpreadGL/backend/run_regression_tests.py)**: The integration test suite that runs 3 automated, end-to-end tests validating continuous, environmental raster, reprojecting/trimming, and asymmetric discrete phylogeographic models.
* **[setup.py](file:///Users/u0150975/Downloads/SpreadGL/backend/setup.py)**: Setup script describing modules and entry points for packaging the toolkit.

### 2. Spatial Layer Generator (`spatial_layer_generator/`)
This module handles parsing and transformation of phylogenetic trees.
* **[spread.py](file:///Users/u0150975/Downloads/SpreadGL/backend/spatial_layer_generator/spread.py)**: The main CLI interface that receives command-line parameters and routes them to continuous or discrete processors.
* **[continuous_space_processor.py](file:///Users/u0150975/Downloads/SpreadGL/backend/spatial_layer_generator/continuous_space_processor.py)**: Processes continuous MCC trees. Parses node heights and coordinates, builds 3D spatial branches, extracts coordinate annotations, and generates HPD (Highest Posterior Density) uncertainty polygons.
* **[discrete_space_processor.py](file:///Users/u0150975/Downloads/SpreadGL/backend/spatial_layer_generator/discrete_space_processor.py)**: Processes discrete MCC trees. Matches node state annotations with location names and resolves them to coordinates.
* **[markov_jump_aggregator.py](file:///Users/u0150975/Downloads/SpreadGL/backend/spatial_layer_generator/markov_jump_aggregator.py)**: Groups transmission events by (start, end) locations. Computes edge weights, resolves coordinates, applies Bayes Factor filtering, and outputs an aggregated migration network.
* **[time_conversion.py](file:///Users/u0150975/Downloads/SpreadGL/backend/spatial_layer_generator/time_conversion.py)**: Utility module for converting dates between decimal years and calendar dates (e.g. `YYYY-MM-DD` or `DD-MM-YYYY`).

### 3. Bayes Factor Test (`bayes_factor_test/`)
Calculates statistical support for discrete migration rates.
* **[rates.py](file:///Users/u0150975/Downloads/SpreadGL/backend/bayes_factor_test/rates.py)**: Computes Bayes Factors (BF) and posterior probabilities from BSSVS indicator columns in the BEAST log. Determines automatically if the model is symmetric or asymmetric.
* **[markov_jump_parser.py](file:///Users/u0150975/Downloads/SpreadGL/backend/bayes_factor_test/markov_jump_parser.py)**: Parses Markov jump count columns (`c_{trait}` or `actual_jumps`) from the BEAST log, applies burn-in, and computes the posterior expected jump counts (MCMC column means). Handles complex location names containing "to" using split-validation.

### 4. Environmental Layer Generator (`environmental_layer_generator/`)
Aligns spatial pathogen data with environmental variables.
* **[regions.py](file:///Users/u0150975/Downloads/SpreadGL/backend/environmental_layer_generator/regions.py)**: Generates regional polygon layers by mapping demographic/environmental data from spreadsheets (CSV) onto a GeoJSON map boundary.
* **[raster.py](file:///Users/u0150975/Downloads/SpreadGL/backend/environmental_layer_generator/raster.py)**: Clips a static climate raster file (TIFF) with a boundary mask and filters coordinates within targeted locations.
* **[rasters.py](file:///Users/u0150975/Downloads/SpreadGL/backend/environmental_layer_generator/rasters.py)**: Processes time-series climate rasters, appending a timestamp to each layer to support dynamic timeline visualizations.

### 5. Projection Transformation (`projection_transformation/`)
* **[reprojection.py](file:///Users/u0150975/Downloads/SpreadGL/backend/projection_transformation/reprojection.py)**: Translates coordinates between coordinate reference systems (e.g., from local projections like EPSG:27700 BNG to web-standard EPSG:4326 WGS84).

### 6. Outlier Detection (`outlier_detection/`)
* **[trimming.py](file:///Users/u0150975/Downloads/SpreadGL/backend/outlier_detection/trimming.py)**: Performs database queries and checks against referenced coordinates to remove empty or invalid data branches.

---

## 🛠️ CLI Tutorials

### 1. Generating Spatial Layers (`spread`)
```bash
spread --tree <tree_file> --time <most_recent_tip_time> --location <location_trait> [options]
```
* `--tree`, `-tr`: Path to NEXUS tree.
* `--time`, `-ti`: Calendar date or decimal year of the latest tip.
* `--location`, `-lo`: Location trait name (e.g. `region` or `coordinates`).
* `--list`, `-li`: Location coordinates list CSV (required for discrete).

### 2. Computing Bayes Factors (`rates`)
```bash
rates --log <beast_log> --location <trait_name> --list <location_csv> --burnin <burnin>
```
* Calculates BFs for discrete migration routes and optionally appends them to a spatial CSV layer using `--layer`.

### 3. Creating Regional Environmental Layers (`regions`)
```bash
regions --data <variables_csv> --locationColumn <col> --map <geojson_map> --locationVariable <prop> --output <output_geojson>
```

### 4. Processing Environmental Rasters (`raster` / `rasters`)
```bash
rasters --data <raster_dir> --map <mask_geojson> --locationVariable <prop> --locationList <states_txt> --output <output_csv>
```

### 5. Reprojecting Coordinates (`reprojection`)
```bash
reprojection --input <input_csv> --lat <lat_cols> --lon <lon_cols> --source <source_epsg> --target <target_epsg> --output <output_csv>
```

### 6. Trimming Outliers (`trimming`)
```bash
trimming --referencing <ref_csv> --foreignkey <foreign_key> --referenced <dataset_csv> --primarykey <primary_key> --null <null_fields> --output <output_csv>
```
