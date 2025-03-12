from typing import Union, Dict
import warnings
import numpy as np
import pandas as pd
from datetime import datetime

import rasters as rt
from rasters import Raster, RasterGeometry

from geos5fp import GEOS5FP

from .constants import *

from .meteorology_conversion import SVP_Pa_from_Ta_C

from .priestley_taylor import GAMMA_PA
from .priestley_taylor import delta_Pa_from_Ta_C

from .vegetation_conversion import LAI_from_NDVI
from .vegetation_conversion import SAVI_from_NDVI
from .vegetation_conversion import fAPAR_from_SAVI
from .vegetation_conversion import fIPAR_from_NDVI

from .partitioning import calculate_relative_surface_wetness
from .partitioning import calculate_green_canopy_fraction
from .partitioning import calculate_plant_moisture_constraint
from .partitioning import calculate_soil_moisture_constraint
from .partitioning import calculate_plant_temperature_constraint

from .partitioning import calculate_soil_net_radiation
from .partitioning import calculate_soil_latent_heat_flux
from .partitioning import calculate_canopy_latent_heat_flux
from .partitioning import calculate_interception

from .fAPARmax import load_fAPARmax
from .Topt import load_Topt

from .net_radiation.verma_net_radiation import process_verma_net_radiation, daily_Rn_integration_verma
from .soil_heat_flux.calculate_SEBAL_soil_heat_flux import calculate_SEBAL_soil_heat_flux


def PTJPL(
        NDVI: Union[Raster, np.ndarray],
        ST_C: Union[Raster, np.ndarray] = None,
        emissivity: Union[Raster, np.ndarray] = None,
        albedo: Union[Raster, np.ndarray] = None,
        Rn: Union[Raster, np.ndarray] = None,
        Ta_C: Union[Raster, np.ndarray] = None,
        RH: Union[Raster, np.ndarray] = None,
        SWin: Union[Raster, np.ndarray] = None,
        G: Union[Raster, np.ndarray] = None,
        Topt: Union[Raster, np.ndarray] = None,
        fAPARmax: Union[Raster, np.ndarray] = None,
        geometry: RasterGeometry = None,
        datetime_UTC: datetime = None,
        GEOS5FP_connection: GEOS5FP = None,
        resampling: str = "nearest",
        delta_Pa: Union[Raster, np.ndarray, float] = None,
        gamma_Pa: Union[Raster, np.ndarray, float] = GAMMA_PA,
        epsilon=None,
        beta_Pa: float = BETA_PA,
        PT_alpha: float = PT_ALPHA,
        minimum_Topt: float = MINIMUM_TOPT,
        floor_Topt: bool = FLOOR_TOPT) -> Dict[str, np.ndarray]:
    results = {}

    if geometry is None and isinstance(NDVI, Raster):
        geometry = NDVI.geometry

    if Topt is None and geometry is not None:
        Topt = load_Topt(geometry)

    if fAPARmax is None and geometry is not None:
        fAPARmax = load_fAPARmax(geometry)

    if GEOS5FP_connection is None:
        GEOS5FP_connection = GEOS5FP()

    if Ta_C is None and geometry is not None and datetime_UTC is not None:
        Ta_C = GEOS5FP_connection.Ta_C(
            time_UTC=datetime_UTC,
            geometry=geometry,
            resampling=resampling
        )

    if Ta_C is None:
        raise ValueError("air temperature (Ta_C) not given")
    
    if RH is None and geometry is not None and datetime_UTC is not None:
        RH = GEOS5FP_connection.RH(
            time_UTC=datetime_UTC,
            geometry=geometry,
            resampling=resampling
        )

    if RH is None:
        raise ValueError("relative humidity (RH) not given")

    if Rn is None and albedo is not None and ST_C is not None and emissivity is not None:
        if SWin is None and geometry is not None and datetime_UTC is not None:
            SWin = GEOS5FP_connection.SWin(
                time_UTC=datetime_UTC,
                geometry=geometry,
                resampling=resampling
            )

        Rn_results = process_verma_net_radiation(
            SWin=SWin,
            albedo=albedo,
            ST_C=ST_C,
            emissivity=emissivity,
            Ta_C=Ta_C,
            RH=RH
        )

        Rn = Rn_results["Rn"]

    if Rn is None:
        raise ValueError("net radiation (Rn) not given")

    if G is None and Rn is not None and ST_C is not None and NDVI is not None and albedo is not None:
        G = calculate_SEBAL_soil_heat_flux(
            Rn=Rn,
            ST_C=ST_C,
            NDVI=NDVI,
            albedo=albedo
        )

    if G is None:
        raise ValueError("soil heat flux (G) not given")

    # calculate meteorology

    # calculate saturation vapor pressure in kPa from air temperature in celsius
    # floor saturation vapor pressure at 1
    SVP_Pa = SVP_Pa_from_Ta_C(Ta_C)

    # constrain relative humidity between 0 and 1
    RH = rt.clip(RH, 0, 1)

    # calculate water vapor pressure in Pascals from relative humidity and saturation vapor pressure
    Ea_Pa = RH * SVP_Pa

    # calculate vapor pressure deficit from water vapor pressure
    VPD_Pa = rt.clip(SVP_Pa - Ea_Pa, 0, None)

    # calculate relative surface wetness from relative humidity
    fwet = calculate_relative_surface_wetness(RH)

    # calculate vegetation values

    # convert normalized difference vegetation index to soil-adjusted vegetation index
    SAVI = SAVI_from_NDVI(NDVI)

    # calculate fraction of absorbed photosynthetically active radiation from soil-adjusted vegetation index
    fAPAR = fAPAR_from_SAVI(SAVI)

    # calculate fIPAR from NDVI
    fIPAR = fIPAR_from_NDVI(NDVI)

    # replace zero fIPAR with NaN
    fIPAR = np.where(fIPAR == 0, np.nan, fIPAR)

    # calculate green canopy fraction (fg) from fAPAR and fIPAR, constrained between zero and one
    fg = calculate_green_canopy_fraction(fAPAR, fIPAR)

    # calculate plant moisture constraint (fM) from fraction of photosynthetically active radiation, constrained between zero and one
    fM = calculate_plant_moisture_constraint(fAPAR, fAPARmax)

    # calculate soil moisture constraint from mean relative humidity and vapor pressure deficit, constrained between zero and one
    fSM = calculate_soil_moisture_constraint(RH, VPD_Pa, beta_Pa=beta_Pa)

    # apply corrections to optimum temperature

    if floor_Topt:
        # when Topt exceeds observed air temperature, then set Topt to match air temperature
        Topt = rt.where(Ta_C > Topt, Ta_C, Topt)

    Topt = rt.clip(Topt, minimum_Topt, None)

    # calculate plant temperature constraint (fT) from optimal phenology
    fT = calculate_plant_temperature_constraint(Ta_C, Topt)

    LAI = LAI_from_NDVI(NDVI)

    # calculate delta / (delta + gamma) term if it's not given
    if epsilon is None:
        # calculate delta if it's not given
        if delta_Pa is None:
            # calculate slope of saturation to vapor pressure curve in kiloPascal per degree Celsius
            delta_Pa = delta_Pa_from_Ta_C(Ta_C)

        # calculate delta / (delta + gamma)
        epsilon = delta_Pa / (delta_Pa + gamma_Pa)

    # soil evaporation

    # caluclate net radiation of the soil from leaf area index
    Rn_soil = calculate_soil_net_radiation(Rn, LAI)
    results["Rn_soil"] = Rn_soil

    # calculate soil evaporation (LEs) from relative surface wetness, soil moisture constraint,
    # priestley taylor coefficient, epsilon = delta / (delta + gamma), net radiation of the soil,
    # and soil heat flux
    LE_soil = calculate_soil_latent_heat_flux(Rn_soil, G, epsilon, fwet, fSM, PT_alpha)
    results["LE_soil"] = LE_soil

    # canopy transpiration

    # calculate net radiation of the canopy from net radiation of the soil
    Rn_canopy = Rn - Rn_soil
    results["Rn_canopy"] = Rn_canopy

    # calculate potential evapotranspiration (pET) from net radiation, and soil heat flux
    PET = PT_alpha * epsilon * (Rn - G)
    results["PET"] = PET

    # calculate canopy transpiration (LEc) from priestley taylor, relative surface wetness,
    # green canopy fraction, plant temperature constraint, plant moisture constraint,
    # epsilon = delta / (delta + gamma), and net radiation of the canopy
    LE_canopy = calculate_canopy_latent_heat_flux(
        Rn_canopy=Rn_canopy,
        epsilon=epsilon,
        fwet=fwet,
        fg=fg,
        fT=fT,
        fM=fM,
        PT_alpha=PT_alpha
    )

    results["LE_canopy"] = LE_canopy

    # interception evaporation

    # calculate interception evaporation (LEi) from relative surface wetness and net radiation of the canopy
    LE_interception = calculate_interception(
        Rn_canopy=Rn_canopy,
        epsilon=epsilon,
        fwet=fwet,
        PT_alpha=PT_alpha
    )

    results["LE_interception"] = LE_interception

    # combined evapotranspiration

    # combine soil evaporation (LEs), canopy transpiration (LEc), and interception evaporation (LEi)
    # into instantaneous evapotranspiration (LE)
    LE = LE_soil + LE_canopy + LE_interception

    # constrain instantaneous evapotranspiration between zero and potential evapotranspiration
    LE = np.clip(LE, 0, PET)
    results["LE"] = LE

    return results
