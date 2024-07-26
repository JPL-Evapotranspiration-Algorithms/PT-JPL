from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

def calculate_relative_surface_wetness(RH: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    This function calculates the relative surface wetness based on the input relative humidity.

    The relative surface wetness is calculated as the fourth power of the relative humidity, 
    which is a common approximation used in hydrology and remote sensing studies.

    Parameters
    ----------
    RH : Union[Raster, np.ndarray]
        The relative humidity as a raster or numpy array. The values should be in the range [0, 1], 
        where 0 represents no humidity and 1 represents 100% humidity.

    Returns
    -------
    Union[Raster, np.ndarray]
        The relative surface wetness as a raster or numpy array. The values will be in the range [0, 1], 
        where 0 represents completely dry and 1 represents completely wet.

    Raises
    ------
    ValueError
        If any value in the RH raster or numpy array is not in the range [0, 1].
    """
    if np.any((RH < 0) | (RH > 1)):
        raise ValueError("Relative humidity values should be in the range [0, 1].")
    return RH ** 4
