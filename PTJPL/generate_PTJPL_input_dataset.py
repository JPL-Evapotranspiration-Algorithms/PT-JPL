import os
import pandas as pd
from PTJPL import process_PTJPL_table
from ECOv002_calval_tables import load_combined_eco_flux_ec_filtered

def generate_PTJPL_input_dataset(output_file_path=None):
    """
    Generates the PTJPL input dataset and saves it to the specified file path.

    Parameters:
        output_file_path (str): The path where the generated CSV file will be saved.
    """
    # Define the default output file path relative to this module's directory
    if output_file_path is None:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        output_file_path = os.path.join(module_dir, "ECOv002-cal-val-PT-JPL-inputs.csv")

    # Load tower data
    tower_data_df = load_combined_eco_flux_ec_filtered()

    # Process the PTJPL table
    processed_data = process_PTJPL_table(tower_data_df)

    # Save to CSV
    processed_data.to_csv(output_file_path, index=False)

    print(f"PTJPL input dataset saved to {output_file_path}")