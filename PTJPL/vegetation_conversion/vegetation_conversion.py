
"""
Vegetation index conversion utilities for remote sensing and land surface modeling.

This module provides functions to convert between NDVI, FVC, LAI, SAVI, fAPAR, and fIPAR using empirical and semi-empirical relationships.
All functions support both Raster and numpy ndarray inputs.
"""
import warnings
from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

# Extinction coefficient for PAR (photosynthetically active radiation)
KPAR = 0.5
# Minimum and maximum values for fIPAR and LAI
MIN_FIPAR = 0.0
MAX_FIPAR = 1.0
MIN_LAI = 0.0
MAX_LAI = 10.0

def FVC_from_NDVI(NDVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Convert Normalized Difference Vegetation Index (NDVI) to Fractional Vegetation Cover (FVC).

    Args:
        NDVI (Raster or np.ndarray): Input NDVI data.

    Returns:
        Raster or np.ndarray: Fractional Vegetation Cover (FVC), clipped to [0, 1].

    Notes:
        NDVIv and NDVIs are empirical values for full vegetation and bare soil, respectively.
    """
    NDVIv = 0.52  # NDVI for full vegetation (empirical)
    NDVIs = 0.04  # NDVI for bare soil (empirical)
    # Linear scaling and clipping to [0, 1]
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

    Args:
        NDVI (Raster or np.ndarray): Input NDVI data.
        min_fIPAR (float): Minimum allowed fIPAR value (default: 0.0).
        max_fIPAR (float): Maximum allowed fIPAR value (default: 1.0).
        min_LAI (float): Minimum allowed LAI value (default: 0.0).
        max_LAI (float): Maximum allowed LAI value (default: 10.0).

    Returns:
        Raster or np.ndarray: Leaf Area Index (LAI), clipped to [min_LAI, max_LAI].

    Notes:
        Uses a Beer-Lambert law relationship with extinction coefficient KPAR.
    """
    # Estimate fraction of intercepted PAR (fIPAR) from NDVI
    fIPAR = rt.clip(NDVI - 0.05, min_fIPAR, max_fIPAR)
    # Set fIPAR=0 to NaN to avoid log(1)
    fIPAR = np.where(fIPAR == 0, np.nan, fIPAR)
    
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        # Beer-Lambert law for LAI
        LAI = rt.clip(-np.log(1 - fIPAR) * (1 / KPAR), min_LAI, max_LAI)
    
    return LAI

def SAVI_from_NDVI(NDVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate Soil-Adjusted Vegetation Index (SAVI) from NDVI.

    Args:
        NDVI (Raster or np.ndarray): Normalized Difference Vegetation Index, typically clipped between 0 and 1.

    Returns:
        Raster or np.ndarray: Soil-Adjusted Vegetation Index (SAVI).

    Notes:
        This is a linear approximation for SAVI.
    """
    return NDVI * 0.45 + 0.132

def fAPAR_from_SAVI(SAVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate fraction of absorbed photosynthetically active radiation (fAPAR) from SAVI.

    Args:
        SAVI (Raster or np.ndarray): Soil-Adjusted Vegetation Index.

    Returns:
        Raster or np.ndarray: Fraction of absorbed PAR, clipped to [0, 1].

    Notes:
        Uses a linear empirical relationship.
    """
    return rt.clip(SAVI * 1.3632 + -0.048, 0, 1)

def fIPAR_from_NDVI(NDVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate fraction of intercepted photosynthetically active radiation (fIPAR) from NDVI.

    Args:
        NDVI (Raster or np.ndarray): Normalized Difference Vegetation Index.

    Returns:
        Raster or np.ndarray: Fraction of intercepted PAR, clipped to [0, 1].

    Notes:
        Empirical linear relationship with NDVI.
    """
    return rt.clip(rt.clip(NDVI, 0, 1) - 0.05, 0, 1)
