"""
Calculate fraction of absorbed photosynthetically active radiation (fAPAR) from SAVI.
"""
from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

def fAPAR_from_SAVI(SAVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate fraction of absorbed photosynthetically active radiation (fAPAR) from SAVI.

    This function uses a linear empirical relationship:
        fAPAR = SAVI * 1.3632 - 0.048
    The result is clipped to the range [0, 1] to ensure valid physical values.

    This approach is commonly used in remote sensing and ecological modeling to estimate vegetation health and productivity from satellite data.

    Reference:
        Fisher, J. B., et al. (2008). "The land surface water and energy budget of the western United States based on MODIS satellite data." Water Resources Research, 44(9), W09422. https://doi.org/10.1029/2007WR006057

    Args:
        SAVI (Raster or np.ndarray): Soil-Adjusted Vegetation Index.

    Returns:
        Raster or np.ndarray: Fraction of absorbed PAR, clipped to [0, 1].
    """
    return rt.clip(SAVI * 1.3632 + -0.048, 0, 1)
