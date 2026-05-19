import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def load_ECOv002_static_tower_PTJPL_inputs() -> gpd.GeoDataFrame:
    """
    Load the input data for the PT-JPL model from the ECOSTRESS Collection 2 Cal-Val dataset.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing the input data with geometry.
    """

    # Define the path to the input CSV file relative to this module's directory
    module_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(module_dir, "ECOv002-static-tower-PT-JPL-inputs.csv")

    # Load the input data into a DataFrame
    inputs_df = pd.read_csv(input_file_path)

    # Ensure the CSV contains a 'geometry' column
    if 'geometry' not in inputs_df.columns:
        raise ValueError("The input CSV must contain a 'geometry' column.")

    # Convert the DataFrame to a GeoDataFrame using the existing geometry column
    inputs_gdf = gpd.GeoDataFrame(
        inputs_df,
        geometry=gpd.GeoSeries.from_wkt(inputs_df['geometry']),
        crs="EPSG:4326"  # Assuming WGS84 coordinate reference system
    )

    return inputs_gdf