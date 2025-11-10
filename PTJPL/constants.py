from priestley_taylor import PT_ALPHA

# Constants used in the PT-JPL model and related calculations.
#
# This module defines key physical and empirical constants for the Priestley-Taylor Jet Propulsion Laboratory (PT-JPL) evapotranspiration model.

RESAMPLING_METHOD = "cubic"

# Beta parameters for soil moisture constraint
# BETA_KPA: beta in units of kPa
# BETA_PA: beta in units of Pa (1 kPa = 1000 Pa)
BETA_KPA = 1.0
BETA_PA = 1000

# Net radiation partitioning coefficient (dimensionless)
KRN = 0.6

# Whether to apply a minimum threshold to Topt (optimum temperature)
FLOOR_TOPT = True

# Minimum allowed value for Topt (if FLOOR_TOPT is True)
MINIMUM_TOPT = 0.1