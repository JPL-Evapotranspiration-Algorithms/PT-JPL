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

from verma_net_radiation import process_verma_net_radiation, daily_Rn_integration_verma
from SEBAL_soil_heat_flux import calculate_SEBAL_soil_heat_flux

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
        time_UTC: datetime = None,
        GEOS5FP_connection: GEOS5FP = None,
        resampling: str = RESAMPLING_METHOD,
        delta_Pa: Union[Raster, np.ndarray, float] = None,
        gamma_Pa: Union[Raster, np.ndarray, float] = GAMMA_PA,
        epsilon=None,
        beta_Pa: float = BETA_PA,
        PT_alpha: float = PT_ALPHA,
        minimum_Topt: float = MINIMUM_TOPT,
        floor_Topt: bool = FLOOR_TOPT) -> Dict[str, np.ndarray]:
    """
    Compute PT-JPL evapotranspiration and its components.

    Parameters:
        NDVI: Normalized Difference Vegetation Index (array or Raster)
        ST_C: Surface temperature in Celsius (array or Raster)
        emissivity: Surface emissivity (array or Raster)
        albedo: Surface albedo (array or Raster)
        Rn: Net radiation (array or Raster)
        Ta_C: Air temperature in Celsius (array or Raster)
        RH: Relative humidity (array or Raster, 0-1)
        SWin: Incoming shortwave radiation (array or Raster)
        G: Soil heat flux (array or Raster)
        Topt: Optimum temperature for photosynthesis (array or Raster)
        fAPARmax: Maximum fraction of absorbed PAR (array or Raster)
        geometry: RasterGeometry object (optional)
        time_UTC: Datetime object for meteorological data (optional)
        GEOS5FP_connection: GEOS5FP object for meteorological data (optional)
        resampling: Resampling method for meteorological data (default "nearest")
        delta_Pa: Slope of saturation vapor pressure curve (optional)
        gamma_Pa: Psychrometric constant (default from constants)
        epsilon: Ratio delta/(delta+gamma) (optional)
        beta_Pa: Soil moisture constraint parameter (default from constants)
        PT_alpha: Priestley-Taylor coefficient (default from constants)
        minimum_Topt: Minimum allowed Topt (default from constants)
        floor_Topt: Whether to floor Topt to Ta_C if Ta_C > Topt (default from constants)

    Returns:
        Dictionary with keys:
            - "Rn_soil": Net radiation to soil
            - "LE_soil": Soil evaporation
            - "Rn_canopy": Net radiation to canopy
            - "PET": Potential evapotranspiration
            - "LE_canopy": Canopy transpiration
            - "LE_interception": Interception evaporation
            - "LE": Total latent heat flux (evapotranspiration)
    """
    results = {}

    # If geometry is not provided, try to infer from NDVI Raster
    if geometry is None and isinstance(NDVI, Raster):
        geometry = NDVI.geometry

    # Load Topt if not provided and geometry is available
    if Topt is None and geometry is not None:
        Topt = load_Topt(geometry)

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
    if Rn is None and albedo is not None and ST_C is not None and emissivity is not None:
        # Retrieve incoming shortwave if not provided
        if SWin is None and geometry is not None and time_UTC is not None:
            SWin = GEOS5FP_connection.SWin(
                time_UTC=time_UTC,
                geometry=geometry,
                resampling=resampling
            )

        # Calculate net radiation using Verma et al. method
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

    # Compute soil heat flux if not provided, using SEBAL method
    if G is None and Rn is not None and ST_C is not None and NDVI is not None and albedo is not None:
        G = calculate_SEBAL_soil_heat_flux(
            Rn=Rn,
            ST_C=ST_C,
            NDVI=NDVI,
            albedo=albedo
        )

    if G is None:
        raise ValueError("soil heat flux (G) not given")

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
    fwet = calculate_relative_surface_wetness(RH)

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
        Topt = rt.where(Ta_C > Topt, Ta_C, Topt)

    # Enforce minimum Topt
    Topt = rt.clip(Topt, minimum_Topt, None)

    # Calculate plant temperature constraint (fT) from Ta_C and Topt
    fT = calculate_plant_temperature_constraint(Ta_C, Topt)

    # Calculate Leaf Area Index (LAI) from NDVI
    LAI = LAI_from_NDVI(NDVI)

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
    Rn_soil = calculate_soil_net_radiation(Rn, LAI)
    results["Rn_soil"] = Rn_soil

    # Calculate soil evaporation (LE_soil)
    LE_soil = calculate_soil_latent_heat_flux(Rn_soil, G, epsilon, fwet, fSM, PT_alpha)
    results["LE_soil"] = LE_soil

    # --- Canopy transpiration ---

    # Net radiation to canopy is total minus soil
    Rn_canopy = Rn - Rn_soil
    results["Rn_canopy"] = Rn_canopy

    # Calculate potential evapotranspiration (PET)
    PET = PT_alpha * epsilon * (Rn - G)
    results["PET"] = PET

    # Calculate canopy transpiration (LE_canopy)
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

    # --- Interception evaporation ---

    # Calculate interception evaporation (LE_interception)
    LE_interception = calculate_interception(
        Rn_canopy=Rn_canopy,
        epsilon=epsilon,
        fwet=fwet,
        PT_alpha=PT_alpha
    )
    results["LE_interception"] = LE_interception

    # --- Combined evapotranspiration ---

    # Total latent heat flux (LE) is sum of soil, canopy, and interception
    LE = LE_soil + LE_canopy + LE_interception

    # Constrain LE between 0 and PET
    LE = np.clip(LE, 0, PET)
    results["LE"] = LE

    return results