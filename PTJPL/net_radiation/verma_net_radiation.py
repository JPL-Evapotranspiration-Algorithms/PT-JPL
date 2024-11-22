from typing import Union, Dict
import warnings
import numpy as np
import rasters as rt
from rasters import Raster

STEFAN_BOLTZMAN_CONSTANT = 5.67036713e-8  # SI units watts per square meter per kelvin to the fourth


def daylight_from_SHA(SHA_deg: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    This function calculates daylight hours from sunrise hour angle in degrees.
    """
    return (2.0 / 15.0) * SHA_deg


def sunrise_from_SHA(SHA_deg: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    This function calculates sunrise hour from sunrise hour angle in degrees.
    """
    return 12.0 - (SHA_deg / 15.0)


def solar_dec_deg_from_day_angle_rad(day_angle_rad: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    This function calculates solar declination in degrees from day angle in radians.
    """
    return (0.006918 - 0.399912 * np.cos(day_angle_rad) + 0.070257 * np.sin(day_angle_rad) - 0.006758 * np.cos(
        2 * day_angle_rad) + 0.000907 * np.sin(2 * day_angle_rad) - 0.002697 * np.cos(
        3 * day_angle_rad) + 0.00148 * np.sin(
        3 * day_angle_rad)) * (180 / np.pi)


def day_angle_rad_from_doy(doy: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    This function calculates day angle in radians from day of year between 1 and 365.
    """
    return (2 * np.pi * (doy - 1)) / 365


def SHA_deg_from_doy_lat(doy: Union[Raster, np.ndarray, int], latitude: np.ndarray) -> Raster:
    """
    This function calculates sunrise hour angle in degrees from latitude in degrees and day of year between 1 and 365.
    """
    # calculate day angle in radians
    day_angle_rad = day_angle_rad_from_doy(doy)

    # calculate solar declination in degrees
    solar_dec_deg = solar_dec_deg_from_day_angle_rad(day_angle_rad)

    # convert latitude to radians
    latitude_rad = np.radians(latitude)

    # convert solar declination to radians
    solar_dec_rad = np.radians(solar_dec_deg)

    # calculate cosine of sunrise angle at latitude and solar declination
    # need to keep the cosine for polar correction
    sunrise_cos = -np.tan(latitude_rad) * np.tan(solar_dec_rad)

    # calculate sunrise angle in radians from cosine
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        sunrise_rad = np.arccos(sunrise_cos)

    # convert to degrees
    sunrise_deg = np.degrees(sunrise_rad)

    # apply polar correction
    sunrise_deg = rt.where(sunrise_cos >= 1, 0, sunrise_deg)
    sunrise_deg = rt.where(sunrise_cos <= -1, 180, sunrise_deg)

    return sunrise_deg

def process_verma_net_radiation(
        SWin: np.ndarray,
        albedo: np.ndarray,
        ST_C: np.ndarray,
        emissivity: np.ndarray,
        Ta_C: np.ndarray,
        RH: np.ndarray,
        cloud_mask: np.ndarray = None) -> Dict:
    results = {}

    # Convert surface temperature from Celsius to Kelvin
    ST_K = ST_C + 273.15

    # Convert air temperature from Celsius to Kelvin
    Ta_K = Ta_C + 273.15

    # Calculate water vapor pressure in Pascals using air temperature and relative humidity
    Ea_Pa = (RH * 0.6113 * (10 ** (7.5 * (Ta_K - 273.15) / (Ta_K - 35.85)))) * 1000
    
    # constrain albedo between 0 and 1
    albedo = np.clip(albedo, 0, 1)

    # calculate outgoing shortwave from incoming shortwave and albedo
    SWout = np.clip(SWin * albedo, 0, None)
    results["SWout"] = SWout

    # calculate instantaneous net radiation from components
    SWnet = np.clip(SWin - SWout, 0, None)

    # calculate atmospheric emissivity
    eta1 = 0.465 * Ea_Pa / Ta_K
    # atmospheric_emissivity = (1 - (1 + eta1) * np.exp(-(1.2 + 3 * eta1) ** 0.5))
    eta2 = -(1.2 + 3 * eta1) ** 0.5
    eta2 = eta2.astype(float)
    eta3 = np.exp(eta2)
    atmospheric_emissivity = np.where(eta2 != 0, (1 - (1 + eta1) * eta3), np.nan)

    if cloud_mask is None:
        # calculate incoming longwave for clear sky
        LWin = atmospheric_emissivity * STEFAN_BOLTZMAN_CONSTANT * Ta_K ** 4
    else:
        # calculate incoming longwave for clear sky and cloudy
        LWin = np.where(
            ~cloud_mask,
            atmospheric_emissivity * STEFAN_BOLTZMAN_CONSTANT * Ta_K ** 4,
            STEFAN_BOLTZMAN_CONSTANT * Ta_K ** 4
        )
    
    results["LWin"] = LWin

    # constrain emissivity between 0 and 1
    emissivity = np.clip(emissivity, 0, 1)

    # calculate outgoing longwave from land surface temperature and emissivity
    LWout = emissivity * STEFAN_BOLTZMAN_CONSTANT * ST_K ** 4
    results["LWout"] = LWout

    # LWnet = np.clip(LWin - LWout, 0, None)
    LWnet = np.clip(LWin - LWout, 0, None)

    # constrain negative values of instantaneous net radiation
    Rn = np.clip(SWnet + LWnet, 0, None)
    results["Rn"] = Rn

    return results

def daily_Rn_integration_verma(
        Rn: Union[Raster, np.ndarray],
        hour_of_day: Union[Raster, np.ndarray],
        doy: Union[Raster, np.ndarray] = None,
        lat: Union[Raster, np.ndarray] = None,
        sunrise_hour: Union[Raster, np.ndarray] = None,
        daylight_hours: Union[Raster, np.ndarray] = None) -> Raster:
    """
    calculate daily net radiation using solar parameters
    this is the average rate of energy transfer from sunrise to sunset
    in watts per square meter
    watts are joules per second
    to get the total amount of energy transferred, factor seconds out of joules
    the number of seconds for which this average is representative is (daylight_hours * 3600)
    documented in verma et al, bisht et al, and lagouARDe et al
    :param Rn:
    :param hour_of_day:
    :param sunrise_hour:
    :param daylight_hours:
    :return:
    """
    if daylight_hours is None or sunrise_hour is None and doy is not None and lat is not None:
        sha_deg = SHA_deg_from_doy_lat(doy, lat)
        daylight_hours = daylight_from_SHA(sha_deg)
        sunrise_hour = sunrise_from_SHA(sha_deg)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        Rn_daily = 1.6 * Rn / (np.pi * np.sin(np.pi * (hour_of_day - sunrise_hour) / (daylight_hours)))
    
    return Rn_daily
