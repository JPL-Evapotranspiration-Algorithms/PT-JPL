from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

from ..constants import PT_ALPHA

def calculate_canopy_latent_heat_flux(
        Rn_canopy: Union[Raster, np.ndarray],
        epsilon: Union[Raster, np.ndarray],
        fwet: Union[Raster, np.ndarray],
        fg: Union[Raster, np.ndarray],
        fT: Union[Raster, np.ndarray],
        fM: Union[Raster, np.ndarray],
        PT_alpha: float = PT_ALPHA) -> Union[Raster, np.ndarray]:
    """
    Calculate the latent heat flux from the canopy (LEc) using the Priestley-Taylor equation, 
    considering various environmental and plant physiological factors.

    Parameters:
    Rn_canopy (Union[Raster, np.ndarray]): Canopy net radiation in watts per square meter. 
        Represents the balance of incoming and outgoing radiation for the canopy.
    epsilon (Union[Raster, np.ndarray]): The Priestley-Taylor parameter. It is the ratio of 
        the slope of the saturation vapor pressure curve to the sum of the slope and 
        psychrometric constant (delta / (delta + gamma)).
    fwet (Union[Raster, np.ndarray]): The relative surface wetness. It ranges from 0 
        (completely dry) to 1 (completely wet). Represents the proportion of the surface 
        that is wet.
    fg (Union[Raster, np.ndarray]): Green canopy fraction. Represents the proportion of 
        the canopy that is green and photosynthetically active.
    fT (Union[Raster, np.ndarray]): Plant temperature constraint. Represents the effect 
        of temperature on plant transpiration.
    fM (Union[Raster, np.ndarray]): Plant moisture constraint. Represents the effect of 
        soil moisture availability on plant transpiration.
    PT_alpha (float, optional): The Priestley-Taylor alpha constant. It is a dimensionless 
        empirical parameter typically equal to 1.26. Defaults to PT_ALPHA.

    Returns:
    Union[Raster, np.ndarray]: The calculated latent heat flux from the canopy (LEc) in 
        watts per square meter. Represents the energy associated with the evapotranspiration 
        process from the canopy.
    """
    return rt.clip(PT_alpha * (1 - fwet) * fg * fT * fM * epsilon * Rn_canopy, 0, None)
