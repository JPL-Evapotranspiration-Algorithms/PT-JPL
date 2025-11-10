import os
import geopandas as gpd
import rasters as rt
from .Topt import load_Topt
from .fAPARmax import load_fAPARmax
from ECOv002_calval_tables import load_combined_eco_flux_ec_filtered, load_metadata_ebc_filt

def generate_static_PTJPL_input_dataset(output_file_path=None):
    """
    Generates the PTJPL static input dataset and saves it to the specified file path.

    Parameters:
        output_file_path (str): The path where the generated CSV file will be saved.
    """
    # Define the default output file path relative to this module's directory
    if output_file_path is None:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        output_file_path = os.path.join(module_dir, "ECOv002-static-tower-PT-JPL-inputs.csv")

    # Load tower metadata
    tower_locations_df = load_metadata_ebc_filt()

    # Extract tower IDs and names
    tower_IDs = list(tower_locations_df["Site ID"])
    tower_names = list(tower_locations_df.Name)

    # Create MultiPoint geometry for tower locations
    tower_points = rt.MultiPoint(
        x=tower_locations_df['Long'].values,
        y=tower_locations_df['Lat'].values
    )

    # Load Topt and fAPARmax values
    Topt_C = load_Topt(geometry=tower_points)
    fAPARmax = load_fAPARmax(geometry=tower_points)

    # Create GeoDataFrame for static data
    tower_static_data_gdf = gpd.GeoDataFrame({
        "ID": tower_IDs,
        "name": tower_names,
        "Topt_C": Topt_C,
        "fAPARmax": fAPARmax,
        "geometry": tower_points
    })

    # Save to CSV
    tower_static_data_gdf.to_csv(output_file_path, index=False)

    print(f"Static PTJPL input dataset saved to {output_file_path}")