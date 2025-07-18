import logging

import numpy as np
import rasters as rt
from dateutil import parser
from pandas import DataFrame

from SEBAL_soil_heat_flux import calculate_SEBAL_soil_heat_flux

from .model import PTJPL
from .Topt import load_Topt
from .fAPARmax import load_fAPARmax

logger = logging.getLogger(__name__)

def process_PTJPL_table(input_df: DataFrame) -> DataFrame:
    """
    Processes a DataFrame containing input variables for the PT-JPL model and returns a DataFrame with PT-JPL outputs.

    This function prepares and validates the required input variables, computes missing variables if needed,
    and runs the PT-JPL model to generate output variables, which are appended to the input DataFrame.

    Args:
        input_df (DataFrame): Input data containing columns required for PT-JPL model computation. Expected columns include:
            - 'ST_C': Surface temperature in Celsius
            - 'NDVI': Normalized Difference Vegetation Index
            - 'albedo': Surface albedo
            - 'Ta_C' or 'Ta': Air temperature in Celsius
            - 'RH': Relative humidity
            - 'Rn': Net radiation
            - 'Topt': Optimum temperature
            - 'fAPARmax': Maximum fraction of absorbed photosynthetically active radiation
            - 'G' (optional): Soil heat flux

    Returns:
        DataFrame: A copy of the input DataFrame with PT-JPL model output columns appended.
    """
    # Convert input columns to numpy arrays of float64 for computation
    ST_C = np.array(input_df.ST_C).astype(np.float64)
    NDVI = np.array(input_df.NDVI).astype(np.float64)

    # Mask NDVI values below vegetation threshold (0.06) as NaN
    NDVI = np.where(NDVI > 0.06, NDVI, np.nan).astype(np.float64)

    albedo = np.array(input_df.albedo).astype(np.float64)

    # Handle air temperature column name differences
    if "Ta_C" in input_df:
        # Use 'Ta_C' if present
        Ta_C = np.array(input_df.Ta_C).astype(np.float64)
    elif "Ta" in input_df:
        # Fallback to 'Ta' if 'Ta_C' is not present
        Ta_C = np.array(input_df.Ta).astype(np.float64)
    else:
        # Raise error if neither air temperature column is present
        raise KeyError("Input DataFrame must contain either 'Ta_C' or 'Ta' column for air temperature.")

    RH = np.array(input_df.RH).astype(np.float64)  # Relative humidity
    Rn = np.array(input_df.Rn).astype(np.float64)  # Net radiation
    Topt = np.array(input_df.Topt).astype(np.float64)  # Optimum temperature
    fAPARmax = np.array(input_df.fAPARmax).astype(np.float64)  # Max fAPAR

    # Mask fAPARmax values of 0 as NaN (invalid)
    fAPARmax = np.where(fAPARmax == 0, np.nan, fAPARmax).astype(np.float64)

    # Soil heat flux (G): use provided or calculate if missing
    if "G" in input_df:
        # Use provided soil heat flux
        G = np.array(input_df.G).astype(np.float64)
    else:
        # Calculate soil heat flux using SEBAL method if not provided
        G = calculate_SEBAL_soil_heat_flux(
            Rn=Rn,
            ST_C=ST_C,
            NDVI=NDVI,
            albedo=albedo
        ).astype(np.float64)

    # Run PT-JPL model with prepared inputs
    results = PTJPL(
        NDVI=NDVI,
        Ta_C=Ta_C,
        RH=RH,
        Rn=Rn,
        Topt=Topt,
        fAPARmax=fAPARmax,
        G=G
    )

    # Copy input DataFrame to avoid modifying original
    output_df = input_df.copy()

    # Append each result from PTJPL model to output DataFrame
    for key, value in results.items():
        output_df[key] = value

    return output_df
