from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

def calculate_plant_temperature_constraint(
        Ta_C: Union[Raster, np.ndarray], 
        Topt: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate the plant temperature constraint (fT) based on the near-surface air temperature and the temperature of optimum phenology.

    This function uses the formula: fT = exp(-((Ta_C - Topt) / Topt)^2) to calculate the plant temperature constraint.

    Parameters:
    Ta_C (Union[Raster, np.ndarray]): The near-surface air temperature in Celsius. Can be a Raster object or a numpy array.
    Topt (Union[Raster, np.ndarray]): The temperature of optimum phenology. Can be a Raster object or a numpy array.

    Returns:
    Union[Raster, np.ndarray]: The calculated plant temperature constraint. The return type will match the input type (Raster or numpy array).
    """
    return np.exp(-(((Ta_C - Topt) / Topt) ** 2))
