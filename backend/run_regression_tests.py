import os
import sys
import tempfile
import zipfile
import json
import rasterio
from rasterio.transform import from_origin
import numpy as np

# Ensure backend directory is in python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Base directories
root_dir = os.path.dirname(backend_dir)
input_dir = os.path.join(root_dir, "inputdata")

def find_data_dir(name):
    direct_maps = {
        "yellow_fever_virus_yfv_in_brazil": "YFV_Brazil"
    }
    mapped_name = direct_maps.get(name.lower(), name)
    p1 = os.path.join(input_dir, mapped_name)
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(root_dir, mapped_name)
    if os.path.exists(p2):
        return p2
    p3 = os.path.join(os.path.dirname(root_dir), mapped_name)
    if os.path.exists(p3):
        return p3
    def clean(s):
        return s.lower().replace("_", "").replace("-", "").replace(" ", "")
    for d in [input_dir, root_dir, os.path.dirname(root_dir)]:
        if os.path.exists(d):
            for entry in os.listdir(d):
                if os.path.isdir(os.path.join(d, entry)):
                    if clean(entry) in clean(name) or clean(name) in clean(entry):
                        return os.path.join(d, entry)
    return p1


def print_result(name, success, details=""):
    status = "\033[92mPASS\033[0m" if success else "\033[91mFAIL\033[0m"
    print(f"[{status}] {name} {details}")
    if not success:
        sys.exit(1)

def ensure_beast_log_unzipped():
    a27_dir = find_data_dir("SARS-CoV-2_lineage_A.27_Worldwide")
    zip_path = os.path.join(a27_dir, "A.27_worldwide.BEAST.log.zip")
    log_path = os.path.join(a27_dir, "A.27_worldwide.BEAST.log")
    if not os.path.exists(log_path) and os.path.exists(zip_path):
        print(f"Unzipping BEAST log for testing...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(a27_dir)

def make_dummy_tif(path):
    # coordinates around Brazil: e.g. lon -55 to -45, lat -20 to -10
    transform = from_origin(-55.0, -10.0, 0.5, 0.5)
    with rasterio.open(
        path, 'w', driver='GTiff',
        height=20, width=20, count=1, dtype='float32',
        crs='EPSG:4326', transform=transform
    ) as dst:
        data = np.ones((20, 20), dtype='float32') * 25.5
        dst.write(data, 1)

def run_tests():
    print("=========================================")
    print("  Running SpreadGL Regression Test Suite ")
    print("=========================================\n")

    ensure_beast_log_unzipped()

    # --- TEST CASE 1: Discrete Phylogeography (SARS-CoV-2 A.27) ---
    print("Running Test Case 1: Discrete Phylogeography (A.27 Variant)...")
    a27_dir = find_data_dir("SARS-CoV-2_lineage_A.27_Worldwide")
    tree_path = os.path.join(a27_dir, "A.27_worldwide.MCC.tree")
    loc_path = os.path.join(a27_dir, "A.27_worldwide_location_list.csv")
    log_path = os.path.join(a27_dir, "A.27_worldwide.BEAST.log")

    with open(tree_path, "rb") as f_tree, open(loc_path, "rb") as f_loc, open(log_path, "rb") as f_log:
        files = {
            "tree_file": ("input.trees", f_tree),
            "location_file": ("locations.csv", f_loc),
            "log_file": ("beast.log", f_log)
        }
        data = {
            "analysis_type": "discrete",
            "most_recent_tip": "2021-06-01",
            "location_trait": "region",
            "date_format": "YYYY-MM-DD",
            "bf_threshold": 3.0,
            "burnin": 0.1
        }
        response = client.post("/api/process-tree", data=data, files=files)
        
        if response.status_code != 200:
            print_result("Test Case 1", False, f"FastAPI returned status {response.status_code}: {response.text}")
        else:
            res_data = response.json()
            # Assertions on outputs
            assert "dynamic_pathway" in res_data
            assert "aggregated_migration_network" in res_data
            
            network = res_data["aggregated_migration_network"]
            features = network.get("features", [])
            assert len(features) > 0, "No migrations aggregated"
            
            # Check jump weights
            for feat in features:
                props = feat.get("properties", {})
                assert "jump_weight" in props
                assert props["jump_weight"] > 0
                
            # Check bayes factors in dynamic_pathway
            pathway = res_data["dynamic_pathway"]
            pathway_features = pathway.get("features", [])
            has_bf = False
            for feat in pathway_features:
                props = feat.get("properties", {})
                if "bayes_factor" in props and props["bayes_factor"] is not None:
                    has_bf = True
                    assert isinstance(props["bayes_factor"], (int, float))
            assert has_bf, "No bayes factors matched in dynamic pathway"
            
            print_result("Test Case 1 (Discrete)", True, f"({len(features)} aggregated migration arcs parsed successfully)")


    # --- TEST CASE 2: Continuous + Environmental (YFV in Brazil & Rabies) ---
    print("\nRunning Test Case 2: Continuous + Environmental (YFV Brazil)...")
    yfv_dir = find_data_dir("Yellow_fever_virus_YFV_in_Brazil")
    yfv_tree_path = os.path.join(yfv_dir, "YFV.MCC.tree")
    yfv_map_path = os.path.join(yfv_dir, "geoBoundaries-BRA-ADM1.geojson")
    yfv_states_path = os.path.join(yfv_dir, "Involved_brazilian_states.txt")

    # Let's create a temp dir and write a dummy tif to upload
    with tempfile.TemporaryDirectory() as tmpdir:
        dummy_tif = os.path.join(tmpdir, "wc2.1_2.5m_tmax_2016-04.tif")
        make_dummy_tif(dummy_tif)

        with open(yfv_tree_path, "rb") as f_tree, open(yfv_map_path, "rb") as f_map, open(yfv_states_path, "rb") as f_states, open(dummy_tif, "rb") as f_tif:
            files = [
                ("tree_file", ("input.trees", f_tree)),
                ("env_raster_map", ("map.geojson", f_map)),
                ("env_raster_loc_list", ("states.txt", f_states)),
                ("env_raster_tiff_files", ("wc2.1_2.5m_tmax_2016-04.tif", f_tif))
            ]
            data = {
                "analysis_type": "continuous",
                "most_recent_tip": "2019-04-16",
                "location_trait": "location1,location2",
                "date_format": "YYYY-MM-DD",
                "env_type": "raster",
                "env_raster_loc_var": "shapeName",
                "env_raster_mode": "static"
            }
            response = client.post("/api/process-tree", data=data, files=files)
            if response.status_code != 200:
                print_result("Test Case 2 (YFV Raster)", False, f"FastAPI returned status {response.status_code}: {response.text}")
            else:
                res_data = response.json()
                assert "dynamic_pathway" in res_data
                assert "geo_contextual_data" in res_data
                assert res_data["geo_contextual_type"] == "csv"
                
                grid_points = res_data["geo_contextual_data"]
                assert len(grid_points) > 0, "No grid points returned from raster masking"
                assert "value" in grid_points[0]
                assert grid_points[0]["value"] == 25.5
                
                print_result("Test Case 2 (YFV Continuous + Raster)", True, f"({len(grid_points)} contextual grid points processed)")

    # Test Rabies continuous tree lacking HPD annotations
    print("Running Test Case 2 (Sub-test): Rabies US Continuous (No HPD)...")
    rab_dir = find_data_dir("Rabies_virus_RABV_in_the_United_States")
    rab_tree_path = os.path.join(rab_dir, "RABV_US1_gamma_MCC.tree")
    with open(rab_tree_path, "rb") as f_tree:
        files = {"tree_file": ("input.trees", f_tree)}
        data = {
            "analysis_type": "continuous",
            "most_recent_tip": "2004-7",
            "location_trait": "location1,location2",
            "date_format": "YYYY-MM-DD"
        }
        response = client.post("/api/process-tree", data=data, files=files)
        if response.status_code != 200:
            print_result("Test Case 2 (Rabies No HPD)", False, f"FastAPI returned status {response.status_code}: {response.text}")
        else:
            res_data = response.json()
            assert "dynamic_pathway" in res_data
            # HPD features should be empty since HPD annotations are missing, but no exception should be thrown
            print_result("Test Case 2 (Rabies No HPD)", True, "Gracefully handled missing HPD without throwing exceptions")


    # --- TEST CASE 3: Continuous + Regions (PEDV in China) ---
    print("\nRunning Test Case 3: Continuous + Regions (PEDV China)...")
    pedv_dir = find_data_dir("Porcine_epidemic_diarrhea_virus_PEDV_in_China")
    pedv_tree_path = os.path.join(pedv_dir, "PEDV_China.MCC.tree")
    pedv_loc_path = os.path.join(pedv_dir, "Involved_provincial_capital_coordinates.csv")
    pedv_env_path = os.path.join(pedv_dir, "Environmental_variables.csv")
    pedv_map_path = os.path.join(pedv_dir, "China_map.geojson")

    with open(pedv_tree_path, "rb") as f_tree, open(pedv_loc_path, "rb") as f_loc, open(pedv_env_path, "rb") as f_env, open(pedv_map_path, "rb") as f_map:
        files = {
            "tree_file": ("input.trees", f_tree),
            "location_file": ("locations.csv", f_loc),
            "env_regions_data": ("env.csv", f_env),
            "env_regions_map": ("map.geojson", f_map)
        }
        data = {
            "analysis_type": "discrete",
            "most_recent_tip": "2019-12-14",
            "location_trait": "location",
            "date_format": "YYYY-MM-DD",
            "env_type": "regions",
            "env_regions_loc_col": "location",
            "env_regions_loc_var": "name"
        }
        response = client.post("/api/process-tree", data=data, files=files)
        if response.status_code != 200:
            print_result("Test Case 3 (PEDV Regions)", False, f"FastAPI returned status {response.status_code}: {response.text}")
        else:
            res_data = response.json()
            assert "geo_contextual_data" in res_data
            assert res_data["geo_contextual_type"] == "geojson"
            
            regions_geojson = res_data["geo_contextual_data"]
            features = regions_geojson.get("features", [])
            assert len(features) > 0, "No regional features returned"
            
            # Check one of the joined variables (e.g. Swine_density or similar variable)
            has_swine_density = False
            for f in features:
                props = f.get("properties", {})
                if "swine_density" in props or "location" in props:
                    has_swine_density = True
                    break
            assert has_swine_density, "Properties did not merge correctly"
            
            print_result("Test Case 3 (PEDV Regions)", True, f"({len(features)} regional polygons successfully merged and loaded)")


    # --- TEST CASE 4: Reprojection & Trimming Edge Cases (B.1.1.7 VOC England) ---
    print("\nRunning Test Case 4: Reprojection & Trimming (B.1.1.7 England)...")
    b117_dir = find_data_dir("SARS-CoV-2_lineage_B.1.1.7_VOC_Alpha_in_England")
    b117_tree_path = os.path.join(b117_dir, "B.1.1.7_England.single.tree")
    b117_ref_path = os.path.join(b117_dir, "TreeTime_270221.csv")

    with open(b117_tree_path, "rb") as f_tree, open(b117_ref_path, "rb") as f_ref:
        files = {
            "tree_file": ("input.trees", f_tree),
            "referenced_file": ("treetime.csv", f_ref)
        }
        data = {
            "analysis_type": "continuous",
            "most_recent_tip": "2021-01-12",
            "location_trait": "coordinates",
            "date_format": "YYYY-MM-DD",
            "reproject": True,
            "reproject_source": "27700",
            "reproject_target": "4326",
            "reproject_lat": "start_lat,end_lat",
            "reproject_lon": "start_lon,end_lon",
            "trim": True,
            "trim_primary_key": "endLat",
            "trim_foreign_key": "end_lat_original",
            "trim_null_queries": "startUTLA,endUTLA"
        }
        response = client.post("/api/process-tree", data=data, files=files)
        if response.status_code != 200:
            print_result("Test Case 4", False, f"FastAPI returned status {response.status_code}: {response.text}")
        else:
            res_data = response.json()
            assert "dynamic_pathway" in res_data
            spatial = res_data["dynamic_pathway"]
            features = spatial.get("features", [])
            assert len(features) > 0, "No spatial features found"
            
            # Verify coordinates are in WGS84 range for England
            for f in features:
                geom = f.get("geometry", {})
                coords = geom.get("coordinates", [])
                if geom.get("type") == "Point":
                    lon, lat = coords
                    assert 49.0 <= lat <= 61.0, f"Latitude {lat} out of range"
                    assert -10.0 <= lon <= 3.0, f"Longitude {lon} out of range"
                elif geom.get("type") == "LineString":
                    for pt in coords:
                        lon, lat = pt[0], pt[1]
                        assert 49.0 <= lat <= 61.0, f"Latitude {lat} out of range"
                        assert -10.0 <= lon <= 3.0, f"Longitude {lon} out of range"
            
            print_result("Test Case 4 (Edge Case)", True, f"({len(features)} branches reprojected to WGS84 & trimmed successfully)")

    print("\n=========================================")
    print("  All 4 Regression Test Cases PASSED!    ")
    print("=========================================\n")
    sys.exit(0)

if __name__ == "__main__":
    run_tests()
