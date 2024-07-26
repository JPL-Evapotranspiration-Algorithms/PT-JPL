from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

# gas constant for dry air in joules per kilogram per kelvin
RD = 286.9

# gas constant for moist air in joules per kilogram per kelvin
RW = 461.5

# specific heat of water vapor in joules per kilogram per kelvin
CPW = 1846.0

# specific heat of dry air in joules per kilogram per kelvin
CPD = 1005.0

def kelvin_to_celsius(T_K: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    convert temperature in kelvin to celsius.
    :param T_K: temperature in kelvin
    :return: temperature in celsius
    """
    return T_K - 273.15

def celcius_to_kelvin(T_C: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    convert temperature in celsius to kelvin.
    :param T_C: temperature in celsius
    :return: temperature in kelvin
    """
    return T_C + 273.15

def calculate_specific_humidity(
        Ea_Pa: Union[Raster, np.ndarray], 
        Ps_Pa: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate the specific humidity of air as a ratio of kilograms of water to kilograms of air.
    
    Args:
        Ea_Pa (Union[Raster, np.ndarray]): Actual water vapor pressure in Pascal.
        surface_pressure_Pa (Union[Raster, np.ndarray]): Surface pressure in Pascal.
    
    Returns:
        Union[Raster, np.ndarray]: Specific humidity in kilograms of water per kilograms of air.
    """
    return ((0.622 * Ea_Pa) / (Ps_Pa - (0.387 * Ea_Pa)))

def calculate_specific_heat(specific_humidity: Union[Raster, np.ndarray]):
    # calculate specific heat capacity of the air (Cp)
    # in joules per kilogram per kelvin
    # from specific heat of water vapor (CPW)
    # and specific heat of dry air (CPD)
    Cp_Jkg = specific_humidity * CPW + (1 - specific_humidity) * CPD

    return Cp_Jkg

def calculate_air_density(
        surface_pressure_Pa: Union[Raster, np.ndarray], 
        Ta_K: Union[Raster, np.ndarray], 
        specific_humidity: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate air density.

    Parameters:
    surface_pressure_Pa (Union[Raster, np.ndarray]): Surface pressure in Pascal.
    Ta_K (Union[Raster, np.ndarray]): Air temperature in Kelvin.
    specific_humidity (Union[Raster, np.ndarray]): Specific humidity.

    Returns:
    Union[Raster, np.ndarray]: Air density in kilograms per cubic meter.
    """
    # numerator: Pa(N / m ^ 2 = kg * m / s ^ 2); denominator: J / kg / K * K)
    rhoD = surface_pressure_Pa / (RD * Ta_K)

    # calculate air density (rho) in kilograms per cubic meter
    rho = rhoD * ((1.0 + specific_humidity) / (1.0 + specific_humidity * (RW / RD)))

    return rho

def SVP_kPa_from_Ta_C(Ta_C: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate the saturation vapor pressure in kiloPascal (kPa) from air temperature in Celsius.

    Parameters:
    Ta_C (Union[Raster, np.ndarray]): Air temperature in Celsius.

    Returns:
    Union[Raster, np.ndarray]: Saturation vapor pressure in kPa.

    """
    SVP_kPa = np.clip(0.611 * np.exp((Ta_C * 17.27) / (Ta_C + 237.7)), 1, None)

    return SVP_kPa

def SVP_Pa_from_Ta_C(Ta_C: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate the saturation vapor pressure in Pascal (Pa) from the air temperature in Celsius (Ta_C).

    Parameters:
        Ta_C (Union[Raster, np.ndarray]): Air temperature in Celsius.

    Returns:
        Union[Raster, np.ndarray]: Saturation vapor pressure in Pascal (Pa).
    """
    return SVP_kPa_from_Ta_C(Ta_C) * 1000

def calculate_surface_pressure(elevation_m: Union[Raster, np.ndarray], Ta_C: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate surface pressure using elevation and air temperature.

    Parameters:
        elevation_m (Union[Raster, np.ndarray]): Elevation in meters.
        Ta_K (Union[Raster, np.ndarray]): Air temperature in Kelvin.

    Returns:
        Union[Raster, np.ndarray]: Surface pressure in Pascal (Pa).
    """
    Ta_K = kelvin_to_celsius(Ta_C)
    Ps_Pa = 101325.0 * (1.0 - 0.0065 * elevation_m / Ta_K) ** (9.807 / (0.0065 * 287.0))  # [Pa]

    return Ps_Pa

