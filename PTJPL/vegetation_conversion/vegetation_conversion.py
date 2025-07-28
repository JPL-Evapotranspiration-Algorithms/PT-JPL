
"""
Vegetation index conversion utilities for remote sensing and land surface modeling.

This module provides functions to convert between NDVI, FVC, LAI, SAVI, fAPAR, and fIPAR using empirical and semi-empirical relationships.
All functions support both Raster and numpy ndarray inputs.
"""

# Import implementations from separate modules
from .SAVI_from_NDVI import SAVI_from_NDVI
from .fAPAR_from_SAVI import fAPAR_from_SAVI
from .fIPAR_from_NDVI import fIPAR_from_NDVI
# Minimum and maximum values for fIPAR and LAI
