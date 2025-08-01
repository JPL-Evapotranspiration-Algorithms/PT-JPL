import numpy as np
from typing import Union
from rasters import Raster

# Default threshold for relative humidity below which surface wetness is set to minimum
# set RH_THRESHOLD to None to emulate ECOSTRESS collection 1 and 2 PT-JPL
RH_THRESHOLD = 0.7
# Default minimum relative surface wetness
# set MIN_FWET to 0.0 to emulate ECOSTRESS collection 1 and 2 PT-JPL
MIN_FWET = 0.0001

def calculate_relative_surface_wetness(
        RH: Union[Raster, np.ndarray], 
        RH_threshold: float = RH_THRESHOLD, 
        min_fwet: float = MIN_FWET) -> Union[Raster, np.ndarray]:
    """
    Estimate relative surface wetness (fwet) as a nonlinear function of atmospheric relative humidity (RH).

    Relative surface wetness (fwet) quantifies the fraction of the land or canopy surface that is wet due to dew, rainfall, or high humidity.
    Wet surfaces promote evaporation, while dry surfaces favor transpiration. This function uses a nonlinear relationship between RH and fwet,
    reflecting the physical process that surface wetness increases rapidly as RH approaches saturation.

    Provenance
    ---------
    - The RH^4 surface wetness algorithm was originally developed for the PT-JPL (Priestley-Taylor Jet Propulsion Laboratory) model (Fisher et al., 2008),
      where it was used to partition latent heat flux into wet and dry components based on atmospheric humidity.
    - MOD16 (Mu et al., 2011) later adopted this approach, adding thresholding and minimum wetness parameters for improved robustness in global remote sensing applications.

    Physical Basis
    -------------
    - As RH approaches 1.0 (saturation), the likelihood of dew formation and wet surfaces increases sharply.
    - The RH^4 relationship models this rapid increase, supported by empirical and theoretical studies.
    - A minimum wetness value (min_fwet) reflects persistent background wetness from dew or residual moisture.
    - The RH threshold (RH_threshold) sets a cutoff below which the surface is considered essentially dry.

    Mathematical Structure
    ---------------------
    - fwet = np.clip(RH ** 4.0, min_fwet, None)
      - RH is relative humidity (0.0 to 1.0, dimensionless).
      - Raising RH to the 4th power models the nonlinear increase in wetness near saturation.
      - Clipped to a minimum value to avoid zero wetness.
    - If RH < RH_threshold, fwet is set to min_fwet (surface is dry below threshold).

    Parameters
    ----------
    RH : Union[Raster, np.ndarray]
        Relative humidity (dimensionless, 0.0 to 1.0).
    RH_threshold : float, optional
        Relative humidity threshold below which surface wetness is set to minimum (default: RH_THRESHOLD).
    min_fwet : float, optional
        Minimum relative surface wetness (default: MIN_FWET).

    Returns
    -------
    Union[Raster, np.ndarray]
        Relative surface wetness (fwet), dimensionless (0.0 to 1.0).

    Notes
    -----
    - Used in MOD16 and PT-JPL evapotranspiration models to partition latent heat flux into wet and dry components.
    - Improves realism in simulating dew formation, rainfall interception, and evaporation.
    - Nonlinear RH^4 relationship and thresholding are supported by peer-reviewed literature and widely used in global ET algorithms.

    References
    ----------
    Mu, Q., Zhao, M., & Running, S. W. (2011). Improvements to a MODIS global terrestrial evapotranspiration algorithm. Remote Sensing of Environment, 115(8), 1781-1800.
    Fisher, J. B., et al. (2008). The land surface water and energy budget of the western United States. Water Resources Research, 44(9).
    Monteith, J. L., & Unsworth, M. H. (2001). Principles of Environmental Physics (3rd ed.). Academic Press.
    Garratt, J. R., & Segal, M. (1988). On the contribution of dew to the surface energy balance. Journal of Applied Meteorology, 27(7), 728-738.

    Example
    -------
        >>> RH = np.array([0.5, 0.8, 0.95, 1.0])
        >>> fwet = calculate_relative_surface_wetness(RH)
        >>> print(fwet)
    """
    fwet = np.float32(np.clip(RH ** 4.0, min_fwet, None))

    if RH_threshold is not None:
        fwet = np.where(RH < RH_threshold, min_fwet, fwet)

    return fwet
