from typing import Union
from os.path import join, abspath, dirname
import numpy as np
import rasters as rt
from rasters import Raster, RasterGeometry, MultiPoint

def load_fAPARmax(geometry: Union[RasterGeometry, MultiPoint]) -> Union[Raster, np.ndarray]:
    """
    Load and return the maximum fraction of absorbed photosynthetically active radiation (fAPARmax)
    for a given geometry from a precomputed raster file.

    Args:
        geometry (RasterGeometry or MultiPoint):
            The spatial geometry (region or points) for which to extract fAPARmax values.

    Returns:
        Raster or np.ndarray: The fAPARmax values for the specified geometry, scaled to [0, 1].
            If a Raster is returned, its nodata value is set to np.nan.
    """
    SCALE_FACTOR = 0.0001  # Scale factor to convert int16 values to float
    # Build the absolute path to the fAPARmax raster file
    filename = join(abspath(dirname(__file__)), "fAPARmax_mean_CMG_int16.tif")
    # Open the raster, extract the region of interest, and apply scaling
    result = rt.clip(rt.Raster.open(filename, geometry=geometry, resampling="cubic") * SCALE_FACTOR, 0, None)

    # If the result is a Raster object, set its nodata value to NaN for consistency
    if isinstance(result, Raster):
        result.nodata = np.nan

    return result
