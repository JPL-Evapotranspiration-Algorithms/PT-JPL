from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

from ..constants import KRN

def calculate_soil_net_radiation(
        Rn: Union[Raster, np.ndarray], 
        LAI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate the soil net radiation based on the total net radiation and leaf area index.

    This function uses the Beer-Lambert law to estimate the soil net radiation. The law states that the absorption of light is logarithmically dependent on the thickness of the medium through which the light is travelling.

    Parameters:
    Rn (Union[Raster, np.ndarray]): The total net radiation. It can be a Raster object or a numpy ndarray.
    LAI (Union[Raster, np.ndarray]): The leaf area index. It can be a Raster object or a numpy ndarray.

    Returns:
    Union[Raster, np.ndarray]: The soil net radiation. The return type will match the input type.

    Note:
    The constant KRN from the module constants is used in the calculation, which is a specific extinction coefficient, 0.6.
    """
    return Rn * np.exp(-KRN * LAI)
