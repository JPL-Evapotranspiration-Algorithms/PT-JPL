"""
Calculate Soil-Adjusted Vegetation Index (SAVI) from NDVI.
"""
from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

def SAVI_from_NDVI(NDVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate Soil-Adjusted Vegetation Index (SAVI) from NDVI.

    This function uses a linear empirical relationship:
        SAVI = NDVI * 0.45 + 0.132
    This is a simplified approximation, not the original SAVI formula, and is used when only NDVI is available but a SAVI-like value is needed for further analysis.

    Reference:
        Huete, A. R. (1988). "A soil-adjusted vegetation index (SAVI)." Remote Sensing of Environment, 25(3), 295–309. https://doi.org/10.1016/0034-4257(88)90106-X

    Args:
        NDVI (Raster or np.ndarray): Normalized Difference Vegetation Index, typically clipped between 0 and 1.

    Returns:
        Raster or np.ndarray: Soil-Adjusted Vegetation Index (SAVI).
    """
    return NDVI * 0.45 + 0.132
