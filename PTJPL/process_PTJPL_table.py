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
    ST_C = np.array(input_df.ST_C).astype(np.float64)
    NDVI = np.array(input_df.NDVI).astype(np.float64)

    NDVI = np.where(NDVI > 0.06, NDVI, np.nan).astype(np.float64)

    albedo = np.array(input_df.albedo).astype(np.float64)
    
    if "Ta_C" in input_df:
        Ta_C = np.array(input_df.Ta_C).astype(np.float64)
    elif "Ta" in input_df:
        Ta_C = np.array(input_df.Ta).astype(np.float64)

    RH = np.array(input_df.RH).astype(np.float64)
    Rn = np.array(input_df.Rn).astype(np.float64)
    Topt = np.array(input_df.Topt).astype(np.float64)
    fAPARmax = np.array(input_df.fAPARmax).astype(np.float64)

    fAPARmax = np.where(fAPARmax == 0, np.nan, fAPARmax).astype(np.float64)

    if "G" in input_df:
        G = np.array(input_df.G).astype(np.float64)
    else:
        G = calculate_SEBAL_soil_heat_flux(
            Rn=Rn,
            ST_C=ST_C,
            NDVI=NDVI,
            albedo=albedo
        ).astype(np.float64)
    
    results = PTJPL(
        NDVI=NDVI,
        Ta_C=Ta_C,
        RH=RH,
        Rn=Rn,
        Topt=Topt,
        fAPARmax=fAPARmax,
        G=G
    )

    output_df = input_df.copy()

    for key, value in results.items():
        output_df[key] = value

    return output_df
