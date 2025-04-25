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
    PTJPL_inputs_from_claval_df:
        Pandas DataFrame containing the columns: tower, lat, lon, time_UTC, albedo, elevation_km
    return:
        Pandas DataFrame containing the columns: tower, lat, lon, time_UTC, doy, albedo, elevation_km, AOT, COT, vapor_gccm, ozone_cm, SZA, KG
    """
    # output_rows = []
    PTJPL_inputs_df = PTJPL_inputs_from_calval_df.copy()

    hour_of_day = []
    doy = []
    Topt = []
    fAPARmax = []

    for i, input_row in PTJPL_inputs_from_calval_df.iterrows():
        tower = input_row.tower
        lat = input_row.lat
        lon = input_row.lon
        time_UTC = input_row.time_UTC
        albedo = input_row.albedo
        elevation_km = input_row.elevation_km
        logger.info(f"collecting PTJPL inputs for tower {tower} lat {lat} lon {lon} time {time_UTC} UTC")
        time_UTC = parser.parse(str(time_UTC))
        time_solar = UTC_to_solar(time_UTC, lon)
        hour_of_day.append(time_solar.hour)
        doy.append(time_UTC.timetuple().tm_yday)
        date_UTC = time_UTC.date()
        
        # tile = sentinel_tiles.toMGRS(lat, lon)[:5]
        # tile_grid = sentinel_tiles.grid(tile=tile, cell_size=70)

        try:
            tile = sentinel_tiles.toMGRS(lat, lon)[:5]
            tile_grid = sentinel_tiles.grid(tile=tile, cell_size=70)
        except Exception as e:
            logger.warning(e)
            Topt.append(np.nan)
            fAPARmax.append(np.nan)
            continue

        rows, cols = tile_grid.shape
        row, col = tile_grid.index_point(rt.Point(lon, lat))
        geometry = tile_grid[max(0, row - 1):min(row + 2, rows - 1),
                             max(0, col - 1):min(col + 2, cols - 1)]

        if not "Topt" in PTJPL_inputs_df.columns:
            try:
                logger.info("generating Topt")
                Topt_value = np.nanmedian(load_Topt(geometry=geometry))
                print(f"Topt: {Topt_value}")
                Topt.append(Topt_value)
            except Exception as e:
                Topt.append(np.nan)
                logger.exception(e)
        
        if not "fAPARmax" in PTJPL_inputs_df.columns:
            try:
                logger.info("generating fAPARmax")
                fAPARmax_value = np.nanmedian(load_fAPARmax(geometry=geometry))
                print(f"fAPARmax: {fAPARmax_value}")
                fAPARmax.append(fAPARmax_value)
            except Exception as e:
                fAPARmax.append(np.nan)
                logger.exception(e)
    
    if not "hour_of_day" in PTJPL_inputs_df.columns:
        PTJPL_inputs_df["hour_of_day"] = hour_of_day

    if not "doy" in PTJPL_inputs_df.columns:
        PTJPL_inputs_df["doy"] = doy
    
    if not "Topt" in PTJPL_inputs_df.columns:
        PTJPL_inputs_df["Topt"] = Topt
    
    if not "fAPARmax" in PTJPL_inputs_df.columns:
        PTJPL_inputs_df["fAPARmax"] = fAPARmax
    
    if "Ta" in PTJPL_inputs_df and "Ta_C" not in PTJPL_inputs_df:
        PTJPL_inputs_df.rename({"Ta": "Ta_C"}, inplace=True)
    
    return PTJPL_inputs_df
