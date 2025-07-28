"""
Calculate fraction of intercepted photosynthetically active radiation (fIPAR) from NDVI.
"""
from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

def fIPAR_from_NDVI(NDVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate fraction of intercepted photosynthetically active radiation (fIPAR) from NDVI.

    This function uses a linear empirical relationship:
        fIPAR = clip(NDVI, 0, 1) - 0.05
    The result is clipped to the range [0, 1] to ensure valid physical values.

    This approach is commonly used in remote sensing to estimate the fraction of sunlight intercepted by vegetation, which is important for ecological and agricultural modeling.

    Reference:
        Gower, S. T., Kucharik, C. J., & Norman, J. M. (1999). "Direct and indirect estimation of leaf area index, fAPAR, and net primary production of terrestrial ecosystems." Remote Sensing of Environment, 70(1), 29–51. https://doi.org/10.1016/S0034-4257(99)00056-7

    Args:
        NDVI (Raster or np.ndarray): Normalized Difference Vegetation Index.

    Returns:
        Raster or np.ndarray: Fraction of intercepted PAR, clipped to [0, 1].
    """
    return rt.clip(rt.clip(NDVI, 0, 1) - 0.05, 0, 1)
