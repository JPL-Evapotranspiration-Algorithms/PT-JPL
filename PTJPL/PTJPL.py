from typing import Union, Dict
import warnings
import numpy as np
import pandas as pd

from .raster import Raster

from .meteorology_conversion.meteorology_conversion import SVP_Pa_from_Ta_C, SVP_kPa_from_Ta_C
from .priestley_taylor.priestley_taylor import GAMMA_KPA, GAMMA_PA, delta_Pa_from_Ta_C, delta_kPa_from_Ta_C
from .vegetation_conversion.vegetation_conversion import LAI_from_NDVI

# Priestley-Taylor coefficient alpha
PT_ALPHA = 1.26

# beta for soil moisture constraint
BETA_KPA = 1.0
BETA_PA = 1000

KRN = 0.6

def process_PTJPL(
            Rn: Union[Raster, np.ndarray],
            G: Union[Raster, np.ndarray],
            NDVI: Union[Raster, np.ndarray],
            Ta_C: Union[Raster, np.ndarray],
            RH: Union[Raster, np.ndarray],
            Topt: Union[Raster, np.ndarray],
            fAPARmax: Union[Raster, np.ndarray],
            delta_Pa: Union[Raster, np.ndarray, float] = None,
            gamma_Pa: Union[Raster, np.ndarray, float] = GAMMA_PA,
            epsilon = None,
            beta_Pa: float = BETA_PA,
            PT_alpha: float = PT_ALPHA) -> Dict[str, np.ndarray]:
        results = {}

        # calculate meteorology

        # calculate saturation vapor pressure in kPa from air temperature in celsius
        # floor saturation vapor pressure at 1
        SVP_Pa = SVP_Pa_from_Ta_C(Ta_C)

        # constrain relative humidity between 0 and 1
        RH = np.clip(RH, 0, 1)

        # calculate water vapor pressure in kilo-Pascals from relative humidity and saturation vapor pressure
        Ea_Pa = RH * SVP_Pa

        # calculate vapor pressure deficit from water vapor pressure
        VPD_Pa = np.clip(SVP_Pa - Ea_Pa, 0, None)

        # calculate relative surface wetness from relative humidity
        fwet = RH ** 4

        # calculate vegetation values

        # calculate fAPAR from NDVI
        SAVI = NDVI * 0.45 + 0.132
        fAPAR = np.clip(SAVI * 1.3632 + -0.048, 0, 1)

        # calculate fIPAR from NDVI
        fIPAR = np.clip(NDVI - 0.05, 0.0, 1.0)

        fIPAR = np.where(fIPAR == 0, np.nan, fIPAR)

        # calculate green canopy fraction (fg) from fAPAR and fIPAR, constrained between zero and one
        # print(np.nanmin(fIPAR), np.nanmax(fIPAR))
        fg = np.where(fIPAR > 0, np.clip(fAPAR / fIPAR, 0.0, 1.0), np.nan)

        # calculate plant moisture constraint (fM) from fraction of photosynthetically active radiation,
        # constrained between zero and one
        # print(np.nanmin(fAPARmax), np.nanmax(fAPARmax))
        fM = np.where(fAPARmax > 0, np.clip(fAPAR / fAPARmax, 0.0, 1.0), np.nan)

        # calculate soil moisture constraint from mean relative humidity and vapor pressure deficit,
        # constrained between zero and one
        fSM = np.clip(RH ** (VPD_Pa / beta_Pa), 0.0, 1.0)
 
        # calculate plant temperature constraint (fT) from optimal phenology
        Topt = np.clip(Topt, 0.1, None)
        fT = np.exp(-(((Ta_C - Topt) / Topt) ** 2))

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
        Rn_soil = Rn * np.exp(-KRN * LAI)
        results["Rn_soil"] = Rn_soil

        # calculate soil evaporation (LEs) from relative surface wetness, soil moisture constraint,
        # priestley taylor coefficient, epsilon = delta / (delta + gamma), net radiation of the soil,
        # and soil heat flux
        LE_soil = np.clip((fwet + fSM * (1 - fwet)) * PT_alpha * epsilon * (Rn_soil - G), 0, None)
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
        LE_canopy = np.clip(PT_alpha * (1 - fwet) * fg * fT * fM * epsilon * Rn_canopy, 0, None)
        results["LE_canopy"] = LE_canopy

        # interception evaporation

        # calculate interception evaporation (LEi) from relative surface wetness and net radiation of the canopy
        LE_interception = np.clip(fwet * PT_alpha * epsilon * Rn_canopy, 0, None)
        results["LE_interception"] = LE_interception

        # combined evapotranspiration

        # combine soil evaporation (LEs), canopy transpiration (LEc), and interception evaporation (LEi)
        # into instantaneous evapotranspiration (LE)
        LE = LE_soil + LE_canopy + LE_interception

        # constrain instantaneous evapotranspiration between zero and potential evapotranspiration        
        LE = np.clip(LE, 0, PET)
        results["LE"] = LE

        return results
