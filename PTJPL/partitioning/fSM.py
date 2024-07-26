from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

from ..constants import BETA_PA

def calculate_soil_moisture_constraint(
        RH: Union[Raster, np.ndarray], 
        VPD_Pa: Union[Raster, np.ndarray], 
        beta_Pa: float = BETA_PA) -> Union[Raster, np.ndarray]:
    """
    Calculates the soil moisture constraint based on relative humidity (RH), 
    vapor pressure deficit (VPD), and a constant beta value.

    The function applies a power law relationship between RH and VPD, 
    and clips the result between 0.0 and 1.0 to ensure the output is within 
    a valid range for soil moisture.

    Parameters:
    RH (Union[Raster, np.ndarray]): Relative humidity between 0 and 1. Can be a Raster object or a numpy array.
    VPD_Pa (Union[Raster, np.ndarray]): The vapor pressure deficit values in Pascals. Can be a Raster object or a numpy array.
    beta_Pa (float, optional): The beta constant in Pascals. Default is 1000 Pa.

    Returns:
    Union[Raster, np.ndarray]: The calculated soil moisture constraint. The output type matches the input type (Raster or numpy array).
    """
    return rt.clip(RH ** (VPD_Pa / beta_Pa), 0.0, 1.0)
