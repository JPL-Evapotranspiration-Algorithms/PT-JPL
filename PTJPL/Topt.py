from typing import Union
from os.path import join, abspath, dirname
import numpy as np
import rasters as rt
from rasters import Raster, RasterGeometry
from rasters import MultiPoint

def load_Topt(geometry: Union[RasterGeometry, MultiPoint]) -> Union[Raster, np.ndarray]:
    SCALE_FACTOR = 0.01
    filename = join(abspath(dirname(__file__)), "Topt_mean_CMG_int16.tif")
    result = rt.clip(rt.Raster.open(filename, geometry=geometry, resampling="cubic") * SCALE_FACTOR, 0, None)
    
    if isinstance(result, Raster):
        result.nodata = np.nan

    return result
