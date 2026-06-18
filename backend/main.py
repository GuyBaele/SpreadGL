import os
import re
import shutil
import tempfile
import geojson
import pandas as pd
import numpy as np
import rasterio
import rioxarray
import geopandas as gpd
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pyproj import Transformer

from spatial_layer_generator.discrete_space_processor import handle_discrete_tree
from spatial_layer_generator.continuous_space_processor import handle_continuous_tree
from spatial_layer_generator.markov_jump_aggregator import aggregate_markov_jumps
from bayes_factor_test.rates import run_bayes_factor_analysis

app = FastAPI(title="SpreadGL API Bridge")

# Enable CORS to allow requests from frontend (usually localhost:8080)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def reproject_geojson_geometry(geometry, transformer):
    if geometry['type'] == 'LineString':
        new_coords = []
        for coord in geometry['coordinates']:
            # transformer.transform(x, y) returns (lon, lat) where x=lon/easting, y=lat/northing
            lon, lat = transformer.transform(coord[0], coord[1])
            new_coord = [lon, lat] + coord[2:]
            new_coords.append(new_coord)
        geometry['coordinates'] = new_coords
    elif geometry['type'] == 'Polygon':
        new_rings = []
        for ring in geometry['coordinates']:
            new_ring = []
            for coord in ring:
                lon, lat = transformer.transform(coord[0], coord[1])
                new_ring.append([lon, lat])
            new_rings.append(new_ring)
        geometry['coordinates'] = new_rings

def reproject_feature_properties(properties, transformer, lat_keys, lon_keys):
    for lat_key, lon_key in zip(lat_keys, lon_keys):
        lat_val = properties.get(lat_key)
        lon_val = properties.get(lon_key)
        if lat_val is not None and lon_val is not None:
            try:
                lon, lat = transformer.transform(float(lon_val), float(lat_val))
                properties[lat_key] = lat
                properties[lon_key] = lon
            except Exception:
                pass

def trim_outliers(branches, trip_features, hpd_features, referenced_df, primary_key, foreign_key, null_fields):
    selected = referenced_df[referenced_df[null_fields].isna().any(axis=1)]
    
    def fmt_val(val):
        try:
            return "{:.5f}".format(float(val))
        except (ValueError, TypeError):
            return str(val).strip()
            
    outlier_keys = set(selected[primary_key].map(fmt_val).tolist())
    
    filtered_branches = []
    filtered_trip_features = []
    filtered_hpd_features = []
    
    for b in branches:
        val = b.get(foreign_key)
        if val is not None and fmt_val(val) in outlier_keys:
            continue
        filtered_branches.append(b)
        
    filtered_branch_ids = set(b['id'] for b in filtered_branches)
    for f in trip_features:
        if f['properties'].get('id') in filtered_branch_ids:
            filtered_trip_features.append(f)
            
    for f in hpd_features:
        if f['properties'].get('id') in filtered_branch_ids:
            filtered_hpd_features.append(f)
            
    return filtered_branches, filtered_trip_features, filtered_hpd_features

def safe_read_file(file_path):
    if str(file_path).lower().endswith(('.geojson', '.json')):
        import json
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'features' in data:
                gdf = gpd.GeoDataFrame.from_features(data['features'])
                gdf.set_crs("EPSG:4326", inplace=True)
                return gdf
        except Exception as e:
            print(f"Warning: safe_read_file custom loader failed ({e}). Falling back to geopandas.read_file.")
    return gpd.read_file(file_path)

def process_regions_geojson(data_file: UploadFile, map_file: UploadFile, location_column: str, location_variable: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        data_path = os.path.join(tmpdir, "data.csv")
        map_path = os.path.join(tmpdir, "map.geojson")
        
        with open(data_path, "wb") as f:
            shutil.copyfileobj(data_file.file, f)
        with open(map_path, "wb") as f:
            shutil.copyfileobj(map_file.file, f)
            
        gdf = safe_read_file(map_path)
        pdf = pd.read_csv(data_path, delimiter=',')
        
        joined_gdf = gdf.merge(pdf, how='left', sort=True, left_on=location_variable, right_on=location_column)
        new_order = [k for k in pdf.keys() if k in joined_gdf.columns] + [k for k in gdf.keys() if k in joined_gdf.columns and k not in pdf.keys()]
        joined_gdf = joined_gdf[new_order]
        
        return joined_gdf.__geo_interface__

def process_rasters_tiff(tiff_files: List[UploadFile], map_file: UploadFile, location_variable: str, location_list_file: UploadFile, mode: str = "static"):
    with tempfile.TemporaryDirectory() as tmpdir:
        map_path = os.path.join(tmpdir, "map.geojson")
        with open(map_path, "wb") as f:
            shutil.copyfileobj(map_file.file, f)
            
        loc_list_path = os.path.join(tmpdir, "locations.txt")
        with open(loc_list_path, "wb") as f:
            shutil.copyfileobj(location_list_file.file, f)
            
        with open(loc_list_path, "r") as f:
            locations = [l.strip() for l in f.read().split(',') if l.strip()]
            
        gdf = safe_read_file(map_path)
        gdf_filtered = gdf.loc[gdf[location_variable].isin(locations)]
        
        if gdf_filtered.empty:
            raise ValueError(f"No matching locations found in the map using variable '{location_variable}' and location list.")
            
        tif_paths = []
        for idx, t_file in enumerate(tiff_files):
            t_path = os.path.join(tmpdir, f"raster_{idx}.tif")
            with open(t_path, "wb") as f:
                shutil.copyfileobj(t_file.file, f)
            tif_paths.append((t_path, t_file.filename))
            
        if mode == "static":
            tif_arrays = []
            for t_path, _ in tif_paths:
                tif_data = rioxarray.open_rasterio(t_path)
                tif_arrays.append(tif_data)
            mean_array = np.mean(tif_arrays, axis=0, dtype=np.float64)
            mean_array_2D = np.squeeze(mean_array, axis=0)
            
            mean_tif = os.path.join(tmpdir, "mean.tif")
            with rasterio.open(tif_paths[0][0]) as src:
                meta = src.meta
            with rasterio.open(mean_tif, 'w', **meta) as dst:
                dst.write(mean_array_2D, 1)
                
            raster = rioxarray.open_rasterio(filename=mean_tif, masked=True)
            clipped = raster.rio.clip(gdf_filtered.geometry)
            masked = clipped.where(np.isfinite(clipped), np.nan)
            
            masked_tif = os.path.join(tmpdir, "masked.tif")
            masked.rio.to_raster(masked_tif)
            
            with rasterio.open(masked_tif) as src:
                raster_data = src.read(1)
                rows, cols = raster_data.shape
                transform = src.transform
                x_coords, y_coords, values = [], [], []
                for row in range(rows):
                    for col in range(cols):
                        val = raster_data[row, col]
                        if np.isfinite(val) and not np.isnan(val):
                            x, y = rasterio.transform.xy(transform, row, col)
                            x_coords.append(x)
                            y_coords.append(y)
                            values.append(float(val))
                            
            df = pd.DataFrame({'longitude': x_coords, 'latitude': y_coords, 'value': values})
            return df.to_dict(orient='records')
            
        else: # dynamic
            x_coords, y_coords, values, timestamps = [], [], [], []
            
            for t_path, original_filename in tif_paths:
                filename = os.path.basename(original_filename)
                m = re.search(r'(\d{4})-(\d{2})', filename)
                if m:
                    year, month = int(m.group(1)), int(m.group(2))
                    dt = datetime(year, month, 15)
                    timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    base = filename.split('.')[0]
                    try:
                        dt = pd.to_datetime(base)
                        timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        continue
                        
                raster = rioxarray.open_rasterio(t_path, masked=True)
                clipped = raster.rio.clip(gdf_filtered.geometry, drop=True)
                masked = clipped.where(np.isfinite(clipped), np.nan)
                
                raster_data = masked.values.squeeze()
                transform = masked.rio.transform()
                
                if len(raster_data.shape) == 3:
                    raster_data = raster_data[0]
                    
                rows, cols = raster_data.shape
                for row in range(rows):
                    for col in range(cols):
                        val = raster_data[row, col]
                        if not np.isnan(val) and np.isfinite(val):
                            x, y = rasterio.transform.xy(transform, row, col)
                            x_coords.append(x)
                            y_coords.append(y)
                            values.append(float(val))
                            timestamps.append(timestamp_str)
                            
            df = pd.DataFrame({'longitude': x_coords, 'latitude': y_coords, 'value': values, 'timestamp': timestamps})
            return df.to_dict(orient='records')

@app.post("/api/process-tree")
async def process_tree(
    analysis_type: str = Form(...),
    most_recent_tip: str = Form(...),
    location_trait: str = Form(...),
    date_format: str = Form("YYYY-MM-DD"),
    bf_threshold: float = Form(3.0),
    burnin: float = Form(0.1),
    
    # Files
    tree_file: UploadFile = File(...),
    log_file: Optional[UploadFile] = File(None),
    location_file: Optional[UploadFile] = File(None),
    
    # Optional Reprojection Parameters
    reproject: bool = Form(False),
    reproject_source: Optional[str] = Form(None),
    reproject_target: Optional[str] = Form(None),
    reproject_lat: Optional[str] = Form(None),
    reproject_lon: Optional[str] = Form(None),
    
    # Optional Trimming Parameters
    trim: bool = Form(False),
    referenced_file: Optional[UploadFile] = File(None),
    trim_primary_key: Optional[str] = Form(None),
    trim_foreign_key: Optional[str] = Form(None),
    trim_null_queries: Optional[str] = Form(None),
    
    # Environmental / External Data Parameters
    env_type: str = Form("none"),  # "none", "regions", "raster"
    env_regions_data: Optional[UploadFile] = File(None),
    env_regions_map: Optional[UploadFile] = File(None),
    env_regions_loc_col: Optional[str] = Form(None),
    env_regions_loc_var: Optional[str] = Form(None),
    
    env_raster_map: Optional[UploadFile] = File(None),
    env_raster_loc_var: Optional[str] = Form(None),
    env_raster_loc_list: Optional[UploadFile] = File(None),
    
    # HPD
    hpd_level: int = Form(80),
    env_raster_mode: Optional[str] = Form("static"),
    env_raster_tiff_files: Optional[List[UploadFile]] = File(None),
):
    # Validation checks
    if analysis_type == "discrete" and location_file is None:
        raise HTTPException(status_code=400, detail="Location CSV required for Discrete analysis")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save tree file
        tree_path = os.path.join(tmpdir, "input.trees")
        with open(tree_path, "wb") as f:
            shutil.copyfileobj(tree_file.file, f)
            
        location_path = None
        if location_file is not None:
            location_path = os.path.join(tmpdir, "locations.csv")
            with open(location_path, "wb") as f:
                shutil.copyfileobj(location_file.file, f)

        # Parse trait locations
        trait_locations = [loc.strip() for loc in location_trait.split(',')]

        hpd_warning = False
        available_hpd_levels = []

        try:
            if analysis_type == "discrete":
                res = handle_discrete_tree(
                    tree_path=tree_path,
                    most_recent_tip=most_recent_tip,
                    date_format=date_format,
                    location=trait_locations,
                    location_list=location_path,
                    extension="geojson",
                    return_data=True
                )
                branches = res["branches"]
                trip_geojson = res["trip_geojson"]
                coordinate_df = res["coordinate_df"]
                
                # Setup basic trip features list
                trip_features = trip_geojson.features
                hpd_features = []
                
            else: # continuous
                res = handle_continuous_tree(
                    tree_path=tree_path,
                    most_recent_tip=most_recent_tip,
                    date_format=date_format,
                    location=trait_locations,
                    extension="geojson",
                    return_data=True
                )
                branches = res["branches"]
                trip_geojson = res["trip_geojson"]
                hpd_geojson = res["hpd_geojson"]
                
                trip_features = trip_geojson.features
                hpd_features = hpd_geojson.features
                coordinate_df = None
                
                if hpd_features:
                    available_hpd_levels = list(set([str(f.properties.get("hpd_level", "80")) for f in hpd_features]))
                
        except ValueError as ve:
            if "Location Mismatch" in str(ve):
                raise HTTPException(status_code=400, detail=str(ve))
            else:
                raise HTTPException(status_code=500, detail=f"Discrete processing value error: {str(ve)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process tree file: {str(e)}")

        # Optional Trimming step
        if trim and referenced_file is not None:
            if not trim_primary_key or not trim_foreign_key or not trim_null_queries:
                raise HTTPException(status_code=400, detail="Missing required parameters for trimming.")
            try:
                referenced_df = pd.read_csv(referenced_file.file)
                null_fields = [f.strip() for f in trim_null_queries.split(',')]
                branches, trip_features, hpd_features = trim_outliers(
                    branches=branches,
                    trip_features=trip_features,
                    hpd_features=hpd_features,
                    referenced_df=referenced_df,
                    primary_key=trim_primary_key,
                    foreign_key=trim_foreign_key,
                    null_fields=null_fields
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Trimming failed: {str(e)}")

        # Optional Reprojection step
        if reproject:
            if not reproject_source or not reproject_target or not reproject_lat or not reproject_lon:
                raise HTTPException(status_code=400, detail="Missing required parameters for CRS reprojection.")
            try:
                source_crs = f"EPSG:{reproject_source}"
                target_crs = f"EPSG:{reproject_target}"
                transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
                
                # Reproject trip geometry & property lat/lon fields
                lat_keys = [k.strip() for k in reproject_lat.split(',')]
                lon_keys = [k.strip() for k in reproject_lon.split(',')]
                
                for f in trip_features:
                    reproject_geojson_geometry(f['geometry'], transformer)
                    reproject_feature_properties(f['properties'], transformer, lat_keys, lon_keys)
                    
                for f in hpd_features:
                    reproject_geojson_geometry(f['geometry'], transformer)
                    reproject_feature_properties(f['properties'], transformer, lat_keys, lon_keys)
                    
                # Update coordinate values inside branches
                for b in branches:
                    for lat_k, lon_k in zip(lat_keys, lon_keys):
                        if b.get(lat_k) is not None and b.get(lon_k) is not None:
                            try:
                                lon, lat = transformer.transform(float(b[lon_k]), float(b[lat_k]))
                                b[lat_k] = lat
                                b[lon_k] = lon
                            except Exception:
                                pass
                                
                # Also reproject coordinate_df for discrete O->D lookup if discrete
                if coordinate_df is not None:
                    for idx, row in coordinate_df.iterrows():
                        try:
                            lon, lat = transformer.transform(float(row['longitude']), float(row['latitude']))
                            coordinate_df.at[idx, 'latitude'] = lat
                            coordinate_df.at[idx, 'longitude'] = lon
                        except Exception:
                            pass
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Reprojection failed: {str(e)}")

        # Assemble collections
        if analysis_type == "continuous":
            hpd_polygons = geojson.FeatureCollection(hpd_features) if hpd_features else geojson.FeatureCollection([])
        else:
            hpd_polygons = None
        dynamic_pathway = geojson.FeatureCollection(trip_features)

        # Build Discrete specific ArcGeoJSON with Markov Jumps
        aggregated_migration_network = None
        if analysis_type == "discrete" and coordinate_df is not None:
            bayes_filter = None
            if log_file is not None:
                try:
                    location_list = coordinate_df['location'].astype(str).tolist()
                    bayes_df = run_bayes_factor_analysis(
                        log_source=log_file.file,
                        location_trait=trait_locations[0],
                        location_list=location_list,
                        burnin=burnin
                    )
                    bayes_filter = {}
                    for _, row in bayes_df.iterrows():
                        key = (str(row['start_name']).strip(), str(row['end_name']).strip())
                        bayes_filter[key] = float(row['bayes_factor'])
                except Exception as e:
                    print(f"Warning: Bayes Factor calculation failed: {str(e)}. Proceeding without filter.")
            
            # Left merge of Bayes Factors into dynamic_pathway features
            if bayes_filter is not None:
                for f in trip_features:
                    start = str(f['properties'].get('start_name', '')).strip()
                    end = str(f['properties'].get('end_name', '')).strip()
                    bf_val = bayes_filter.get((start, end))
                    if bf_val is None:
                        bf_val = bayes_filter.get((end, start))
                    f['properties']['bayes_factor'] = bf_val
            
            try:
                aggregated_migration_network = aggregate_markov_jumps(
                    branches=branches,
                    coordinate_df=coordinate_df,
                    bayes_filter=bayes_filter,
                    bf_threshold=bf_threshold
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Markov Jump aggregation failed: {str(e)}")

        # Environmental Preprocessing
        geo_contextual_data = None
        geo_contextual_type = None
        
        if env_type == "regions":
            if env_regions_data is not None and env_regions_map is not None and env_regions_loc_col and env_regions_loc_var:
                try:
                    geo_contextual_data = process_regions_geojson(
                        data_file=env_regions_data,
                        map_file=env_regions_map,
                        location_column=env_regions_loc_col,
                        location_variable=env_regions_loc_var
                    )
                    geo_contextual_type = "geojson"
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Regions polygons processing failed: {str(e)}")
            else:
                raise HTTPException(status_code=400, detail="Missing required parameters for regional environmental data processing.")
                
        elif env_type == "raster":
            if env_raster_map is not None and env_raster_loc_var and env_raster_loc_list is not None and env_raster_tiff_files:
                try:
                    geo_contextual_data = process_rasters_tiff(
                        tiff_files=env_raster_tiff_files,
                        map_file=env_raster_map,
                        location_variable=env_raster_loc_var,
                        location_list_file=env_raster_loc_list,
                        mode=env_raster_mode or "static"
                    )
                    geo_contextual_type = "csv"
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Raster TIFF processing failed: {str(e)}")
            else:
                raise HTTPException(status_code=400, detail="Missing required parameters for environmental raster TIFF processing.")

        return {
            "analysis_type": analysis_type,
            "hpd_polygons": hpd_polygons,
            "hpd_warning": hpd_warning,
            "available_hpd_levels": available_hpd_levels,
            "dynamic_pathway": dynamic_pathway,
            "aggregated_migration_network": aggregated_migration_network,
            "geo_contextual_data": geo_contextual_data,
            "geo_contextual_type": geo_contextual_type
        }
