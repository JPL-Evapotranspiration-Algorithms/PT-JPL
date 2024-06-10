from os.path import join, abspath, dirname
import numpy as np
import raster as rt
from raster import Raster, RasterGeometry

def load_Topt(geometry: RasterGeometry) -> Raster:
    SCALE_FACTOR = 0.01
    filename = join(abspath(dirname(__file__)), "Topt_mean_CMG_int16.tif")
    image = rt.clip(rt.Raster.open(filename, geometry=geometry, resampling="cubic") * SCALE_FACTOR, 0, None)
    image.nodata = np.nan

    return image