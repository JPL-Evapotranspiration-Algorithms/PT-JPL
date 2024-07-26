from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

def calculate_plant_moisture_constraint(
        fAPAR: Union[Raster, np.ndarray], 
        fAPARmax: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate the plant moisture constraint (fM) based on the fraction of photosynthetically active radiation (fAPAR) and its maximum value (fAPARmax).

    The plant moisture constraint is calculated as the ratio of fAPAR to fAPARmax, clipped between 0.0 and 1.0. If fAPARmax is 0, the function returns NaN.

    Parameters:
    fAPAR (Union[Raster, np.ndarray]): The fraction of photosynthetically active radiation absorbed by green vegetation. It can be a Raster object or a numpy array.
    fAPARmax (Union[Raster, np.ndarray]): The maximum fraction of photosynthetically active radiation that can be absorbed by green vegetation. It can be a Raster object or a numpy array.

    Returns:
    Union[Raster, np.ndarray]: The plant moisture constraint, calculated as the ratio of fAPAR to fAPARmax. The result is a Raster object if the inputs are Raster objects, otherwise it is a numpy array.
    """
    return np.where(fAPARmax > 0, np.clip(fAPAR / fAPARmax, 0.0, 1.0), np.nan)
