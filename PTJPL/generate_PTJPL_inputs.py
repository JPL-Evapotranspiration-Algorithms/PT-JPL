import logging

import numpy as np
import rasters as rt
from dateutil import parser
from pandas import DataFrame
from sentinel_tiles import sentinel_tiles
from solar_apparent_time import UTC_to_solar

from .model import PTJPL
from .Topt import load_Topt
from .fAPARmax import load_fAPARmax

logger = logging.getLogger(__name__)

def generate_PTJPL_inputs(PTJPL_inputs_from_calval_df: DataFrame) -> DataFrame:
    """
    Generate and augment PT-JPL model input variables from a calibration/validation DataFrame.

    This function processes a DataFrame containing site and observation metadata, computes additional variables
    required for the PT-JPL model (such as hour of day, day of year, Topt, and fAPARmax), and returns an augmented DataFrame.

    Args:
        PTJPL_inputs_from_calval_df (DataFrame):
            Pandas DataFrame containing at least the columns: 'tower', 'lat', 'lon', 'time_UTC', 'albedo', 'elevation_km'.

    Returns:
        DataFrame: Augmented DataFrame with additional columns for PT-JPL model input, including:
            - 'hour_of_day': Solar hour of day
            - 'doy': Day of year
            - 'Topt': Optimum temperature (if not already present)
            - 'fAPARmax': Maximum fAPAR (if not already present)
            - 'Ta_C': Air temperature in Celsius (renamed from 'Ta' if needed)
    """
    # Make a copy to avoid modifying the original DataFrame
    PTJPL_inputs_df = PTJPL_inputs_from_calval_df.copy()

    # Lists to store computed values for each row
    hour_of_day = []  # Solar hour of day
    doy = []          # Day of year
    Topt = []         # Optimum temperature
    fAPARmax = []     # Maximum fAPAR

    # Iterate over each row to compute additional variables
    for i, input_row in PTJPL_inputs_from_calval_df.iterrows():
        tower = input_row.tower
        lat = input_row.lat
        lon = input_row.lon
        time_UTC = input_row.time_UTC
        albedo = input_row.albedo
        elevation_km = input_row.elevation_km

        # Log the current site and time being processed
        logger.info(f"collecting PTJPL inputs for tower {tower} lat {lat} lon {lon} time {time_UTC} UTC")

        # Parse time_UTC string to datetime object
        time_UTC = parser.parse(str(time_UTC))

        # Convert UTC time to solar time using longitude
        time_solar = UTC_to_solar(time_UTC, lon)
        hour_of_day.append(time_solar.hour)

        # Compute day of year
        doy.append(time_UTC.timetuple().tm_yday)
        date_UTC = time_UTC.date()

        # Attempt to determine the Sentinel tile and grid for the site
        try:
            tile = sentinel_tiles.toMGRS(lat, lon)[:5]
            tile_grid = sentinel_tiles.grid(tile=tile, cell_size=70)
        except Exception as e:
            # If tile lookup fails, log warning and append NaN for Topt and fAPARmax
            logger.warning(e)
            Topt.append(np.nan)
            fAPARmax.append(np.nan)
            continue

        # Find the grid cell containing the site
        rows, cols = tile_grid.shape
        row, col = tile_grid.index_point(rt.Point(lon, lat))
        # Define a 3x3 geometry window around the site (with bounds checking)
        geometry = tile_grid[max(0, row - 1):min(row + 2, rows - 1),
                             max(0, col - 1):min(col + 2, cols - 1)]

        # If Topt is not already present, compute it for the site
        if not "Topt" in PTJPL_inputs_df.columns:
            try:
                logger.info("generating Topt")
                Topt_value = np.nanmedian(load_Topt(geometry=geometry))
                print(f"Topt: {Topt_value}")
                Topt.append(Topt_value)
            except Exception as e:
                Topt.append(np.nan)
                logger.exception(e)

        # If fAPARmax is not already present, compute it for the site
        if not "fAPARmax" in PTJPL_inputs_df.columns:
            try:
                logger.info("generating fAPARmax")
                fAPARmax_value = np.nanmedian(load_fAPARmax(geometry=geometry))
                print(f"fAPARmax: {fAPARmax_value}")
                fAPARmax.append(fAPARmax_value)
            except Exception as e:
                fAPARmax.append(np.nan)
                logger.exception(e)

    # Add computed columns to DataFrame if not already present
    if not "hour_of_day" in PTJPL_inputs_df.columns:
        PTJPL_inputs_df["hour_of_day"] = hour_of_day

    if not "doy" in PTJPL_inputs_df.columns:
        PTJPL_inputs_df["doy"] = doy

    if not "Topt" in PTJPL_inputs_df.columns:
        PTJPL_inputs_df["Topt"] = Topt

    if not "fAPARmax" in PTJPL_inputs_df.columns:
        PTJPL_inputs_df["fAPARmax"] = fAPARmax

    # Rename 'Ta' to 'Ta_C' if present and not already renamed
    if "Ta" in PTJPL_inputs_df and "Ta_C" not in PTJPL_inputs_df:
        PTJPL_inputs_df.rename({"Ta": "Ta_C"}, inplace=True)

    return PTJPL_inputs_df
