from typing import Union
import numpy as np

from rasters import Raster

# psychrometric constant gamma in kiloPascal per degree Celsius
# same as value for ventilated (Asmann type) psychrometers, with an air movement of some 5 m/s
# http://www.fao.org/docrep/x0490e/x0490e07.htm
GAMMA_KPA = 0.0662  # kPa/C

# psychrometric constant gamma in Pascal per degree Celsius
GAMMA_PA = GAMMA_KPA * 1000

def delta_kPa_from_Ta_C(Ta_C: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    return 4098 * (0.6108 * np.exp(17.27 * Ta_C / (237.7 + Ta_C))) / (Ta_C + 237.3) ** 2

def delta_Pa_from_Ta_C(Ta_C: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    return delta_kPa_from_Ta_C(Ta_C) * 1000

def calculate_epsilon(delta: Union[Raster, np.ndarray], gamma: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    return delta / (delta + gamma)

def epsilon_from_Ta_C(Ta_C: Union[Raster, np.ndarray], gamma_Pa: Union[Raster, np.ndarray, float] = GAMMA_PA) -> Union[Raster, np.ndarray]:
    delta_Pa = delta_Pa_from_Ta_C(Ta_C)
    epsilon = calculate_epsilon(delta=delta_Pa, gamma=gamma_Pa)

    return epsilon
