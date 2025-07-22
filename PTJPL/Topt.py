from typing import Union
from os.path import join, abspath, dirname
import numpy as np
import rasters as rt
from rasters import Raster, RasterGeometry
from rasters import MultiPoint

def load_Topt(geometry: Union[RasterGeometry, MultiPoint]) -> Union[Raster, np.ndarray]:
    """
    Load the optimal temperature (Topt) raster data for a given geometry.

    This function reads the 'Topt_mean_CMG_int16.tif' raster file, clips it to the provided geometry,
    applies a scale factor, and ensures that nodata values are set to NaN for consistency.

    Args:
        geometry (Union[RasterGeometry, MultiPoint]): The geometry to which the raster should be clipped.
            This can be a RasterGeometry or a MultiPoint object.

    Returns:
        Union[Raster, np.ndarray]: The clipped and scaled Topt raster as a Raster object or a NumPy array,
            depending on the input geometry.

    Notes:
        - The raster values are multiplied by a scale factor of 0.01 to convert to the correct units.
        - Nodata values in the output Raster are set to np.nan.
    """
    SCALE_FACTOR = 0.01  # Scale factor to convert raster values to correct units

    # Construct the absolute path to the Topt raster file
    filename = join(abspath(dirname(__file__)), "Topt_mean_CMG_int16.tif")

    # Open the raster, clip to the provided geometry, apply cubic resampling, and scale the values
    result = rt.clip(
        rt.Raster.open(filename, geometry=geometry, resampling="cubic") * SCALE_FACTOR,
        0,  # Minimum value to clip to
        None  # No maximum value clipping
    )

    # If the result is a Raster object, set its nodata value to np.nan for consistency
    if isinstance(result, Raster):
        result.nodata = np.nan

    return result
