"""
Priestley-Taylor model utilities for evapotranspiration calculations.

This module provides functions to compute the slope of the saturation vapor pressure curve (delta),
the psychrometric constant (gamma), and the Priestley-Taylor epsilon parameter, all of which are
used in the Priestley-Taylor equation for estimating potential evapotranspiration.
"""

from typing import Union
import numpy as np
from rasters import Raster

# Psychrometric constant gamma in kiloPascal per degree Celsius (kPa/°C)
# Value for ventilated (Asmann type) psychrometers, with air movement ~5 m/s
# Reference: http://www.fao.org/docrep/x0490e/x0490e07.htm
GAMMA_KPA = 0.0662  # kPa/°C

# Psychrometric constant gamma in Pascal per degree Celsius (Pa/°C)
GAMMA_PA = GAMMA_KPA * 1000

def delta_kPa_from_Ta_C(Ta_C: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate the slope of the saturation vapor pressure curve (delta) in kPa/°C from air temperature.

    Args:
        Ta_C (Raster or np.ndarray): Air temperature in degrees Celsius.

    Returns:
        Raster or np.ndarray: Slope of the saturation vapor pressure curve (delta) in kPa/°C.
    """
    # Formula from FAO-56, Allen et al. (1998)
    return 4098 * (0.6108 * np.exp(17.27 * Ta_C / (237.7 + Ta_C))) / (Ta_C + 237.3) ** 2

def delta_Pa_from_Ta_C(Ta_C: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate the slope of the saturation vapor pressure curve (delta) in Pa/°C from air temperature.

    Args:
        Ta_C (Raster or np.ndarray): Air temperature in degrees Celsius.

    Returns:
        Raster or np.ndarray: Slope of the saturation vapor pressure curve (delta) in Pa/°C.
    """
    return delta_kPa_from_Ta_C(Ta_C) * 1000

def calculate_epsilon(delta: Union[Raster, np.ndarray], gamma: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate the Priestley-Taylor epsilon parameter (dimensionless).

    Args:
        delta (Raster or np.ndarray): Slope of the saturation vapor pressure curve (Pa/°C or kPa/°C).
        gamma (Raster or np.ndarray): Psychrometric constant (same units as delta).

    Returns:
        Raster or np.ndarray: Priestley-Taylor epsilon parameter (dimensionless).
    """
    return delta / (delta + gamma)

def epsilon_from_Ta_C(Ta_C: Union[Raster, np.ndarray], gamma_Pa: Union[Raster, np.ndarray, float] = GAMMA_PA) -> Union[Raster, np.ndarray]:
    """
    Calculate Priestley-Taylor epsilon parameter from air temperature.

    Args:
        Ta_C (Raster or np.ndarray): Air temperature in degrees Celsius.
        gamma_Pa (Raster, np.ndarray, or float): Psychrometric constant in Pa/°C (default: GAMMA_PA).

    Returns:
        Raster or np.ndarray: Priestley-Taylor epsilon parameter (dimensionless).
    """
    delta_Pa = delta_Pa_from_Ta_C(Ta_C)
    epsilon = calculate_epsilon(delta=delta_Pa, gamma=gamma_Pa)
    return epsilon
