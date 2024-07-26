
from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

from ..constants import PT_ALPHA

def calculate_interception(
        Rn_canopy: Union[Raster, np.ndarray],
        epsilon: Union[Raster, np.ndarray],
        fwet: Union[Raster, np.ndarray],
        PT_alpha: float = PT_ALPHA) -> Union[Raster, np.ndarray]:
    """
    Calculates the PT-JPL interception evaporation (LEi) based on the relative surface wetness and the net radiation of the canopy.

    This function uses the Priestley-Taylor equation for evaporation estimation, which is given by:

    $$ LEi = fwet * PT_alpha * epsilon * Rn_canopy $$

    The result is clipped to ensure that evaporation does not exceed the available energy.

    Parameters:
    Rn_canopy (Union[Raster, np.ndarray]): The net radiation at the canopy level, given in watts per square meter (W/m^2). 
        This represents the balance between incoming and outgoing radiation for the canopy.
    epsilon (Union[Raster, np.ndarray]): The Priestley-Taylor parameter, which is the ratio of the slope of the saturation 
        vapor pressure curve to the sum of the slope and the psychrometric constant (delta / (delta + gamma)).
    fwet (Union[Raster, np.ndarray]): The relative surface wetness, ranging from 0 (completely dry) to 1 (completely wet). 
        This represents the proportion of the surface that is wet.
    PT_alpha (float, optional): The Priestley-Taylor alpha constant. This is a dimensionless empirical parameter, 
        typically equal to 1.26. Defaults to PT_ALPHA.

    Returns:
    Union[Raster, np.ndarray]: The calculated interception evaporation (LEi), given in the same units as the input parameters.
    """
    return rt.clip(fwet * PT_alpha * epsilon * Rn_canopy, 0, None)
