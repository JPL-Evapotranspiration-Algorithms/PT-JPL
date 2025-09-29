"""
PT-JPL Model Implementation

This module provides the implementation of the PT-JPL (Priestley-Taylor Jet Propulsion Laboratory) model
for estimating evapotranspiration and its components using remote sensing and meteorological data.

The main function, PTJPL, computes instantaneous latent heat fluxes (evapotranspiration) and its partitioning
into soil evaporation, canopy transpiration, and interception evaporation, based on a variety of input parameters
including NDVI, surface temperature, albedo, net radiation, air temperature, relative humidity, and more.

Dependencies:
    - numpy
    - pandas
    - rasters
    - GEOS5FP
    - verma_net_radiation
    - SEBAL_soil_heat_flux
    - PTJPL internal modules (constants, meteorology_conversion, priestley_taylor, vegetation_conversion, partitioning, fAPARmax, Topt)

Returns:
    Dictionary containing arrays for each calculated component (e.g., LE, LE_soil, LE_canopy, LE_interception, PET, etc.)
"""

from typing import Union, Dict
import warnings
import numpy as np
import pandas as pd
from datetime import datetime

import rasters as rt
from rasters import Raster, RasterGeometry

from GEOS5FP import GEOS5FP

from carlson_leaf_area_index import carlson_leaf_area_index

from meteorology_conversion import SVP_Pa_from_Ta_C

from verma_net_radiation import verma_net_radiation, daylight_Rn_integration_verma
from daylight_evapotranspiration import daylight_ET_from_instantaneous_LE
from sun_angles import calculate_daylight
from SEBAL_soil_heat_flux import calculate_SEBAL_soil_heat_flux

from priestley_taylor import GAMMA_PA
from priestley_taylor import delta_Pa_from_Ta_C

from .constants import *

from .vegetation_conversion import SAVI_from_NDVI
from .vegetation_conversion import fAPAR_from_SAVI
from .vegetation_conversion import fIPAR_from_NDVI

from .partitioning import RH_THRESHOLD, MIN_FWET
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

def PTJPL(
    NDVI: Union[Raster, np.ndarray],
    ST_C: Union[Raster, np.ndarray] = None,
    emissivity: Union[Raster, np.ndarray] = None,
    albedo: Union[Raster, np.ndarray] = None,
    Rn_Wm2: Union[Raster, np.ndarray] = None,
    Ta_C: Union[Raster, np.ndarray] = None,
    RH: Union[Raster, np.ndarray] = None,
    SWin_Wm2: Union[Raster, np.ndarray] = None,
    G_Wm2: Union[Raster, np.ndarray] = None,
    Topt_C: Union[Raster, np.ndarray] = None,
    fAPARmax: Union[Raster, np.ndarray] = None,
    geometry: RasterGeometry = None,
    time_UTC: datetime = None,
    GEOS5FP_connection: GEOS5FP = None,
    resampling: str = RESAMPLING_METHOD,
    delta_Pa: Union[Raster, np.ndarray, float] = None,
    gamma_Pa: Union[Raster, np.ndarray, float] = GAMMA_PA,
    epsilon: Union[Raster, np.ndarray, float] = None,
    beta_Pa: float = BETA_PA,
    PT_alpha: float = PT_ALPHA,
    minimum_Topt: float = MINIMUM_TOPT,
    RH_threshold: float = RH_THRESHOLD,
    min_fwet: float = MIN_FWET,
    floor_Topt: bool = FLOOR_TOPT,
    upscale_to_daylight: bool = False,
    day_of_year: np.ndarray = None) -> Dict[str, np.ndarray]:
    """
    Computes instantaneous latent heat fluxes (evapotranspiration) and its partitioning into soil evaporation, canopy transpiration, and interception evaporation using the PT-JPL model.

    Parameters
    ----------
    NDVI : Raster or np.ndarray
        Normalized Difference Vegetation Index.
    ST_C : Raster or np.ndarray, optional
        Surface temperature in Celsius.
    emissivity : Raster or np.ndarray, optional
        Surface emissivity.
    albedo : Raster or np.ndarray, optional
        Surface albedo.
    Rn_Wm2 : Raster or np.ndarray, optional
        Net radiation (W/m^2).
    Ta_C : Raster or np.ndarray, optional
        Air temperature in Celsius.
    RH : Raster or np.ndarray, optional
        Relative humidity (0-1).
    SWin_Wm2 : Raster or np.ndarray, optional
        Incoming shortwave radiation (W/m^2).
    G_Wm2 : Raster or np.ndarray, optional
        Soil heat flux (W/m^2).
    Topt_C : Raster or np.ndarray, optional
        Optimum temperature for photosynthesis (C).
    fAPARmax : Raster or np.ndarray, optional
        Maximum fraction of absorbed PAR.
    geometry : RasterGeometry, optional
        Geometry for spatial data.
    time_UTC : datetime, optional
        UTC time for meteorological data.
    GEOS5FP_connection : GEOS5FP, optional
        Connection for meteorological data.
    resampling : str, optional
        Resampling method for meteorological data (default from constants).
    delta_Pa : Raster, np.ndarray, or float, optional
        Slope of saturation vapor pressure curve.
    gamma_Pa : Raster, np.ndarray, or float, optional
        Psychrometric constant (default from constants).
    epsilon : Raster, np.ndarray, or float, optional
        Ratio delta/(delta+gamma).
    beta_Pa : float, optional
        Soil moisture constraint parameter (default from constants).
    PT_alpha : float, optional
        Priestley-Taylor coefficient (default from constants).
    minimum_Topt : float, optional
        Minimum allowed Topt (default from constants).
    RH_threshold : float, optional
        Relative humidity threshold for surface wetness (default: 0.7). Set None to disable thresholding.
    min_FWET : float, optional
        Minimum relative surface wetness (default: 0.0001). Set 0.0 to emulate ECOSTRESS collection 1/2.
    floor_Topt : bool, optional
        If True, floor Topt to Ta_C if Ta_C > Topt (default from constants).

    Returns
    -------
    Dict[str, np.ndarray]
        Dictionary containing:
            'Rn_soil' : Net radiation to soil (W/m^2)
            'LE_soil' : Soil evaporation (W/m^2)
            'Rn_canopy' : Net radiation to canopy (W/m^2)
            'PET' : Potential evapotranspiration (W/m^2)
            'LE_canopy' : Canopy transpiration (W/m^2)
            'LE_interception' : Interception evaporation (W/m^2)
            'LE' : Total latent heat flux (evapotranspiration, W/m^2)
            If upscale_to_daylight=True and time_UTC is provided:
                'Rn_daylight' : Net radiation during daylight (W/m^2)
                'LE_daylight' : Latent heat flux during daylight (W/m^2)
                'ET_daylight_kg' : Daylight ET in kg/m^2
    """
    results = {}

    # If geometry is not provided, try to infer from NDVI Raster
    if geometry is None and isinstance(NDVI, Raster):
        geometry = NDVI.geometry

    # Load Topt if not provided and geometry is available
    if Topt_C is None and geometry is not None:
        Topt_C = load_Topt(geometry)

    # Load fAPARmax if not provided and geometry is available
    if fAPARmax is None and geometry is not None:
        fAPARmax = load_fAPARmax(geometry)

    # Create GEOS5FP connection if not provided
    if GEOS5FP_connection is None:
        GEOS5FP_connection = GEOS5FP()

    # Retrieve air temperature if not provided, using GEOS5FP and geometry/time
    if Ta_C is None and geometry is not None and time_UTC is not None:
        Ta_C = GEOS5FP_connection.Ta_C(
            time_UTC=time_UTC,
            geometry=geometry,
            resampling=resampling
        )

    if Ta_C is None:
        raise ValueError("air temperature (Ta_C) not given")
    
    # Retrieve relative humidity if not provided, using GEOS5FP and geometry/time
    if RH is None and geometry is not None and time_UTC is not None:
        RH = GEOS5FP_connection.RH(
            time_UTC=time_UTC,
            geometry=geometry,
            resampling=resampling
        )

    if RH is None:
        raise ValueError("relative humidity (RH) not given")

    # Compute net radiation if not provided, using albedo, ST_C, and emissivity
    if Rn_Wm2 is None and albedo is not None and ST_C is not None and emissivity is not None:
        # Retrieve incoming shortwave if not provided
        if SWin_Wm2 is None and geometry is not None and time_UTC is not None:
            SWin_Wm2 = GEOS5FP_connection.SWin(
                time_UTC=time_UTC,
                geometry=geometry,
                resampling=resampling
            )

        # Calculate net radiation using Verma et al. method
        Rn_results = verma_net_radiation(
            SWin_Wm2=SWin_Wm2,
            albedo=albedo,
            ST_C=ST_C,
            emissivity=emissivity,
            Ta_C=Ta_C,
            RH=RH,
            geometry=geometry,
            time_UTC=time_UTC,
            resampling=resampling,
            GEOS5FP_connection=GEOS5FP_connection
        )

        Rn_Wm2 = Rn_results["Rn_Wm2"]

    if Rn_Wm2 is None:
        raise ValueError("net radiation (Rn) not given")

    # Compute soil heat flux if not provided, using SEBAL method
    if G_Wm2 is None and Rn_Wm2 is not None and ST_C is not None and NDVI is not None and albedo is not None:
        G_Wm2 = calculate_SEBAL_soil_heat_flux(
            Rn=Rn_Wm2,
            ST_C=ST_C,
            NDVI=NDVI,
            albedo=albedo
        )

    if G_Wm2 is None:
        raise ValueError("soil heat flux (G) not given")
    
    results["G_Wm2"] = G_Wm2    

    # --- Meteorological calculations ---

    # Calculate saturation vapor pressure (Pa) from air temperature (C)
    SVP_Pa = SVP_Pa_from_Ta_C(Ta_C)

    # Constrain relative humidity between 0 and 1
    RH = rt.clip(RH, 0, 1)

    # Calculate actual vapor pressure (Pa)
    Ea_Pa = RH * SVP_Pa

    # Calculate vapor pressure deficit (Pa), floor at 0
    VPD_Pa = rt.clip(SVP_Pa - Ea_Pa, 0, None)

    # Calculate relative surface wetness from RH
    fwet = calculate_relative_surface_wetness(
        RH=RH,
        RH_threshold=RH_threshold,
        min_fwet=min_fwet
    )

    # --- Vegetation calculations ---

    # Convert NDVI to Soil-Adjusted Vegetation Index (SAVI)
    SAVI = SAVI_from_NDVI(NDVI)

    # Calculate fraction of absorbed PAR (fAPAR) from SAVI
    fAPAR = fAPAR_from_SAVI(SAVI)

    # Calculate fraction of intercepted PAR (fIPAR) from NDVI
    fIPAR = fIPAR_from_NDVI(NDVI)

    # Replace zero fIPAR with NaN to avoid division by zero
    fIPAR = np.where(fIPAR == 0, np.nan, fIPAR)

    # Calculate green canopy fraction (fg), constrained between 0 and 1
    fg = calculate_green_canopy_fraction(fAPAR, fIPAR)

    # Calculate plant moisture constraint (fM), constrained between 0 and 1
    fM = calculate_plant_moisture_constraint(fAPAR, fAPARmax)

    # Calculate soil moisture constraint (fSM), constrained between 0 and 1
    fSM = calculate_soil_moisture_constraint(RH, VPD_Pa, beta_Pa=beta_Pa)

    # --- Optimum temperature corrections ---

    if floor_Topt:
        # If Topt exceeds observed air temperature, set Topt to Ta_C
        Topt_C = rt.where(Ta_C > Topt_C, Ta_C, Topt_C)

    # Enforce minimum Topt
    Topt_C = rt.clip(Topt_C, minimum_Topt, None)

    # Calculate plant temperature constraint (fT) from Ta_C and Topt
    fT = calculate_plant_temperature_constraint(Ta_C, Topt_C)

    # Calculate Leaf Area Index (LAI) from NDVI
    LAI = carlson_leaf_area_index(NDVI)

    # --- Priestley-Taylor epsilon calculation ---

    if epsilon is None:
        # Calculate delta if not provided
        if delta_Pa is None:
            # Slope of saturation vapor pressure curve (Pa/C)
            delta_Pa = delta_Pa_from_Ta_C(Ta_C)

        # Calculate epsilon = delta / (delta + gamma)
        epsilon = delta_Pa / (delta_Pa + gamma_Pa)

    # --- Soil evaporation ---

    # Calculate net radiation to soil from LAI
    Rn_soil_Wm2 = calculate_soil_net_radiation(Rn_Wm2, LAI)
    results["Rn_soil_Wm2"] = Rn_soil_Wm2

    # Calculate soil evaporation (LE_soil)
    LE_soil_Wm2 = calculate_soil_latent_heat_flux(Rn_soil_Wm2, G_Wm2, epsilon, fwet, fSM, PT_alpha)
    results["LE_soil_Wm2"] = LE_soil_Wm2

    # --- Canopy transpiration ---

    # Net radiation to canopy is total minus soil
    Rn_canopy_Wm2 = Rn_Wm2 - Rn_soil_Wm2
    results["Rn_canopy_Wm2"] = Rn_canopy_Wm2

    # Calculate potential evapotranspiration (PET)
    PET_Wm2 = PT_alpha * epsilon * (Rn_Wm2 - G_Wm2)
    results["PET_Wm2"] = PET_Wm2

    # Calculate canopy transpiration (LE_canopy)
    LE_canopy_Wm2 = calculate_canopy_latent_heat_flux(
        Rn_canopy=Rn_canopy_Wm2,
        epsilon=epsilon,
        fwet=fwet,
        fg=fg,
        fT=fT,
        fM=fM,
        PT_alpha=PT_alpha
    )
    results["LE_canopy_Wm2"] = LE_canopy_Wm2

    # --- Interception evaporation ---

    # Calculate interception evaporation (LE_interception)
    LE_interception_Wm2 = calculate_interception(
        Rn_canopy=Rn_canopy_Wm2,
        epsilon=epsilon,
        fwet=fwet,
        PT_alpha=PT_alpha
    )
    results["LE_interception_Wm2"] = LE_interception_Wm2

    # --- Combined evapotranspiration ---

    # Total latent heat flux (LE) is sum of soil, canopy, and interception
    LE_Wm2 = LE_soil_Wm2 + LE_canopy_Wm2 + LE_interception_Wm2

    # Constrain LE between 0 and PET
    LE_Wm2 = np.clip(LE_Wm2, 0, PET_Wm2)
    results["LE_Wm2"] = LE_Wm2

    # --- Daylight upscaling ---
    if upscale_to_daylight and time_UTC is not None:
        # Use new upscaling function from daylight_evapotranspiration
        daylight_results = daylight_ET_from_instantaneous_LE(
            LE_instantaneous_Wm2=LE_Wm2,
            Rn_instantaneous_Wm2=Rn_Wm2,
            G_instantaneous_Wm2=G_Wm2,
            day_of_year=day_of_year,
            time_UTC=time_UTC,
            geometry=geometry
        )
        # Add all returned daylight results to output
        results.update(daylight_results)

    return results
