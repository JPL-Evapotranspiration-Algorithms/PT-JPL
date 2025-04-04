from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

KPAR = 0.5
MIN_FIPAR = 0.0
MAX_FIPAR = 1.0
MIN_LAI = 0.0
MAX_LAI = 10.0

def FVC_from_NDVI(NDVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Convert Normalized Difference Vegetation Index (NDVI) to Fractional Vegetation Cover (FVC).

    Parameters:
        NDVI (Union[Raster, np.ndarray]): Input NDVI data.

    Returns:
        Union[Raster, np.ndarray]: Converted FVC data.
    """
    NDVIv = 0.52  # +- 0.03
    NDVIs = 0.04  # +- 0.03
    FVC = rt.clip((NDVI - NDVIs) / (NDVIv - NDVIs), 0.0, 1.0)

    return FVC

def LAI_from_NDVI(
        NDVI: Union[Raster, np.ndarray],
        min_fIPAR: float = MIN_FIPAR,
        max_fIPAR: float = MAX_FIPAR,
        min_LAI: float = MIN_LAI,
        max_LAI: float = MAX_LAI) -> Union[Raster, np.ndarray]:
    """
    Convert Normalized Difference Vegetation Index (NDVI) to Leaf Area Index (LAI).

    Parameters:
        NDVI (Union[Raster, np.ndarray]): Input NDVI data.

    Returns:
        Union[Raster, np.ndarray]: Converted LAI data.
    """
    fIPAR = rt.clip(NDVI - 0.05, min_fIPAR, max_fIPAR)
    fIPAR = np.where(fIPAR == 0, np.nan, fIPAR)
    LAI = rt.clip(-np.log(1 - fIPAR) * (1 / KPAR), min_LAI, max_LAI)

    return LAI

def SAVI_from_NDVI(NDVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Linearly calculates Soil-Adjusted Vegetation Index from ST_K.
    :param NDVI: normalized difference vegetation index clipped between 0 and 1
    :return: soil-adjusted vegetation index
    """
    return NDVI * 0.45 + 0.132

def fAPAR_from_SAVI(SAVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Linearly calculates fraction of absorbed photosynthetically active radiation from soil-adjusted vegetation index.
    :param SAVI: soil adjusted vegetation index
    :return: fraction of absorbed photosynthetically active radiation
    """
    return rt.clip(SAVI * 1.3632 + -0.048, 0, 1)

def fIPAR_from_NDVI(NDVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate fraction of intercepted photosynthetically active radiation from normalized difference vegetation index
    :param NDVI: normalized difference vegetation index
    :return: fraction of intercepted photosynthetically active radiation
    """
    return rt.clip(rt.clip(NDVI, 0, 1) - 0.05, 0, 1)
