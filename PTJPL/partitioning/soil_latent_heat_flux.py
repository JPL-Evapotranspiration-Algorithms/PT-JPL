from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

from ..constants import PT_ALPHA

def calculate_soil_latent_heat_flux(
        Rn_soil: Union[Raster, np.ndarray], 
        G: Union[Raster, np.ndarray], 
        epsilon: Union[Raster, np.ndarray], 
        fwet: Union[Raster, np.ndarray], 
        fSM: Union[Raster, np.ndarray], 
        PT_alpha: float = PT_ALPHA) -> Union[Raster, np.ndarray]:
    """
    Calculate the Priestley-Taylor Jet Propulsion Laboratory (PT-JPL) soil latent heat flux.

    Parameters:
    Rn_soil (Union[Raster, np.ndarray]): The soil net radiation in watts per square meter (W/m^2). It represents the balance of incoming and outgoing radiation.
    G (Union[Raster, np.ndarray]): The soil heat flux in watts per square meter (W/m^2). It represents the amount of heat moving into or out of the soil.
    epsilon (Union[Raster, np.ndarray]): The ratio of the slope of the saturation vapor pressure curve to the sum of the slope and psychrometric constant (delta / (delta + gamma)).
    fwet (Union[Raster, np.ndarray]): The relative surface wetness. It ranges from 0 (completely dry) to 1 (completely wet).
    fSM (Union[Raster, np.ndarray]): The soil moisture constraint. It represents the effect of soil moisture on evapotranspiration.
    PT_alpha (float, optional): The Priestley-Taylor alpha constant. It is a dimensionless empirical parameter typically equal to 1.26. Defaults to PT_ALPHA.

    Returns:
    Union[Raster, np.ndarray]: The calculated soil latent heat flux in watts per square meter (W/m^2). It represents the energy associated with the phase change of water in the soil.

    The function uses the PT-JPL model to estimate the soil latent heat flux based on the input parameters. The calculation is clipped at zero to avoid negative values which are physically meaningless in this context.
    """
    return np.clip((fwet + fSM * (1 - fwet)) * PT_alpha * epsilon * (Rn_soil - G), 0, None)
