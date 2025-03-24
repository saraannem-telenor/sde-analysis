import os
import rioxarray
import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from rioxarray.merge import merge_arrays


STATKRAFT_CRS = "EPSG:32633"
REAL_CRS = "EPSG:32633"
ALTIMETRI_CRS = "EPSG:25832"
CERRA_CRS = "EPSG:4326"



def extract_elevation_for_catchment(
    dem_dir: str,
    shapefile_path: str,
    save_path: str = "catchment_terrain_dem.tif"
) -> pd.DataFrame:
    """
    Clips all DEM files in a directory to a catchment area, merges them,
    and returns a DataFrame with elevation, latitude, and longitude.

    Parameters:
    - dem_dir: folder containing .tif DEM files
    - shapefile_path: path to the catchment shapefile
    - save_path: output .tif path for the merged and clipped DEM

    Returns:
    - elevation_df: DataFrame with columns [x, y, elevation, latitude, longitude]
    """

    # Load and project catchment shapefile
    catchment = gpd.read_file(shapefile_path).to_crs(ALTIMETRI_CRS)

    dem_files = [f for f in os.listdir(dem_dir) if f.endswith(".tif")]
    elevation_dfs = []
    dem_clipped_list = []

    for fname in dem_files:
        fpath = os.path.join(dem_dir, fname)
        dem = rioxarray.open_rasterio(fpath, masked=True)

        # Skip DEMs that don't intersect the catchment
        bounds = dem.rio.bounds()
        dem_box = gpd.GeoDataFrame(geometry=[box(*bounds)], crs=dem.rio.crs)
        if not dem_box.intersects(catchment.union_all()).any():
            continue

        # Clip and convert to DataFrame
        dem_clipped = dem.rio.clip(catchment.geometry, catchment.crs)
        dem_clipped_list.append(dem_clipped)

        df = dem_clipped.squeeze().to_dataframe(name="elevation").reset_index()
        df = df.dropna(subset=["elevation"])
        elevation_dfs.append(df)

    if not dem_clipped_list:
        raise ValueError("No overlapping DEM tiles found.")

    # Reproject to ensure consistent orientation before merging
    reference = dem_clipped_list[0]
    dem_clipped_list_aligned = [
        da.sortby(["y", "x"]).rio.reproject_match(reference) for da in dem_clipped_list
    ]

    merged_dem = merge_arrays(dem_clipped_list_aligned)
    merged_dem.rio.to_raster(save_path)

    # Convert elevation DataFrame to lat/lon
    elevation_df = pd.concat(elevation_dfs, ignore_index=True)
    gdf = gpd.GeoDataFrame(
        elevation_df,
        geometry=gpd.points_from_xy(elevation_df['x'], elevation_df['y']),
        crs=ALTIMETRI_CRS).to_crs(CERRA_CRS)

    gdf['latitude'] = gdf.geometry.y
    gdf['longitude'] = gdf.geometry.x

    return gdf.drop(columns='geometry')


if __name__ == "__main__":
    DEM_DIR = "../data/raw/other_data/altimetri"
    SHAPEFILE = "../data/raw/catchment_statkraft/catchment.shp"
    DEM_OUT = "../data/processed/catchment_terrain_dem.tif"
    CSV_OUT = "../data/processed/elevation_data.csv"

    df = extract_elevation_for_catchment(DEM_DIR, SHAPEFILE, DEM_OUT)
    df.to_csv(CSV_OUT, index=False)

    print(f"Saved elevation data to {CSV_OUT}")
