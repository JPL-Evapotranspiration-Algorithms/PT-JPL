# Priestley-Taylor Jet Propulsion Laboratory (PT-JPL) Evapotranspiration Model Python Implementation

[![CI](https://github.com/JPL-Evapotranspiration-Algorithms/PT-JPL/actions/workflows/ci.yml/badge.svg)](https://github.com/JPL-Evapotranspiration-Algorithms/PT-JPL/actions/workflows/ci.yml)

This software package is a Python implementation of the Priestley-Taylor Jet Propulsion Laboratory (PT-JPL) model of evapotranspiration. It was re-implemented in Python by Gregory Halverson at Jet Propulsion Laboratory based on MATLAB code produced by Joshua Fisher. The PT-JPL model extends the classical Priestley-Taylor equation with explicit partitioning of latent heat flux into canopy transpiration, interception evaporation, and soil evaporation, along with biophysical constraint functions for operational remote sensing applications.

The software was developed as part of a research grant by the NASA Research Opportunities in Space and Earth Sciences (ROSES) program. It was designed for use by the Ecosystem Spaceborne Thermal Radiometer Experiment on Space Station (ECOSTRESS) mission as a precursor for the Surface Biology and Geology (SBG) mission. However, it may also be useful for general remote sensing and GIS projects in Python. This package can be utilized for remote sensing research in Jupyter notebooks and deployed for operations in data processing pipelines.

The software is being released according to the SPD-41 open-science requirements of NASA-funded ROSES projects.

[Gregory H. Halverson](https://github.com/gregory-halverson-jpl) (they/them)<br>
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)<br>
Lead developer<br>
NASA Jet Propulsion Laboratory 329G

Joshua B. Fisher (he/him)<br>
[jbfisher@chapman.edu](mailto:jbfisher@chapman.edu)<br>
Algorithm inventor<br>
Chapman University
 
Claire Villanueva-Weeks (she/her)<br>
[claire.s.villanueva-weeks@jpl.nasa.gov](mailto:claire.s.villanueva-weeks@jpl.nasa.gov)<br>
Code maintenance<br>
NASA Jet Propulsion Laboratory 329G

## Installation

```
pip install PTJPL
```

## Scientific Methodology

### Theoretical Foundation

The PT-JPL model builds upon the foundational Priestley-Taylor equation but extends it significantly for operational remote sensing applications. While the classical Priestley-Taylor approach estimates potential evapotranspiration under well-watered conditions, PT-JPL explicitly accounts for vegetation stress, soil moisture limitations, and surface wetness variations through biophysical constraint functions derived from remote sensing observations.

### Key Differences: PT-JPL vs. Classical Priestley-Taylor

| Aspect | Classical Priestley-Taylor | PT-JPL Model |
|--------|---------------------------|--------------|
| **Scope** | Potential ET estimation | Actual ET with component partitioning |
| **Water Stress** | Assumes well-watered conditions | Explicit moisture and temperature constraints |
| **Spatial Resolution** | Point or uniform application | Pixel-level remote sensing implementation |
| **Components** | Single bulk ET estimate | Soil evaporation + canopy transpiration + interception |
| **Inputs** | Meteorological variables only | Remote sensing + meteorological data |
| **Surface Heterogeneity** | Homogeneous surface assumption | Accounts for vegetation cover variations |

### Core PT-JPL Equations

The PT-JPL model partitions total evapotranspiration into three components:

<div align="center">

**LE<sub>total</sub> = LE<sub>soil</sub> + LE<sub>canopy</sub> + LE<sub>interception</sub>**

</div>

Where each component is calculated using modified Priestley-Taylor equations with biophysical constraints:

#### 1. Soil Evaporation

<div align="center">

**LE<sub>soil</sub> = α × ε × (Rn<sub>soil</sub> - G) × f<sub>wet</sub> × f<sub>SM</sub>**

</div>

Where:
- **LE_soil** = Soil evaporation [W m⁻²]
- **α** = Priestley-Taylor coefficient (1.26) [dimensionless]
- **ε** = Energy partitioning coefficient [dimensionless]
- **Rn_soil** = Net radiation reaching soil surface [W m⁻²]
- **G** = Soil heat flux [W m⁻²]
- **f_wet** = Relative surface wetness [0-1]
- **f_SM** = Soil moisture constraint [0-1]

#### 2. Canopy Transpiration

<div align="center">

**LE<sub>canopy</sub> = α × ε × Rn<sub>canopy</sub> × (1 - f<sub>wet</sub>) × f<sub>g</sub> × f<sub>T</sub> × f<sub>M</sub>**

</div>

Where:
- **LE_canopy** = Canopy transpiration [W m⁻²]
- **Rn_canopy** = Net radiation absorbed by canopy [W m⁻²]
- **f_g** = Green canopy fraction [0-1]
- **f_T** = Plant temperature constraint [0-1]
- **f_M** = Plant moisture constraint [0-1]

#### 3. Interception Evaporation

<div align="center">

**LE<sub>interception</sub> = α × ε × Rn<sub>canopy</sub> × f<sub>wet</sub>**

</div>

Where:
- **LE_interception** = Interception evaporation from wet canopy surfaces [W m⁻²]

### Biophysical Constraint Functions

#### Energy Partitioning Coefficient (ε)

Following classical Priestley-Taylor methodology:

<div align="center">

**ε = Δ / (Δ + γ)**

</div>

Where:
- **Δ** = Slope of saturation vapor pressure curve [Pa °C⁻¹]
- **γ** = Psychrometric constant (66.2 Pa °C⁻¹)

<div align="center">

**Δ = [4098 × (0.6108 × exp(17.27 × T<sub>a</sub> / (237.3 + T<sub>a</sub>)))] / (T<sub>a</sub> + 237.3)<sup>2</sup>**

</div>

#### Net Radiation Partitioning

<div align="center">

**Rn<sub>soil</sub> = Rn × exp(-k × LAI)**

</div>

<div align="center">

**Rn<sub>canopy</sub> = Rn - Rn<sub>soil</sub>**

</div>

Where:
- **k** = Light extinction coefficient (≈0.5) [dimensionless]
- **LAI** = Leaf Area Index derived from NDVI using Carlson method

#### Surface Wetness Function (f_wet)

<div align="center">

**f<sub>wet</sub> = RH<sup>4</sup>** &nbsp;&nbsp;&nbsp;&nbsp; (for RH > RH<sub>threshold</sub>, default 0.7)

</div>

<div align="center">

**f<sub>wet</sub> = min<sub>f_wet</sub>** &nbsp;&nbsp;&nbsp;&nbsp; (for RH ≤ RH<sub>threshold</sub>, default 0.0001)

</div>

Where:
- **RH** = Relative humidity [0-1]
- **RH_threshold** = Threshold for wet surface conditions
- **min_f_wet** = Minimum surface wetness to avoid zero values

#### Green Canopy Fraction (f_g)

<div align="center">

**f<sub>g</sub> = min(fAPAR / fIPAR, 1.0)**

</div>

Where:
- **fAPAR** = Fraction of absorbed photosynthetically active radiation
- **fIPAR** = Fraction of intercepted photosynthetically active radiation

Vegetation indices are converted as:

<div align="center">

**SAVI = [1.5 × (NDVI + 0.5)] / (NDVI + 0.5 + 1.0)**

</div>

<div align="center">

**fAPAR = 1.3632 × SAVI - 0.048** &nbsp;&nbsp;&nbsp;&nbsp; (Fisher et al., 2008)

</div>

<div align="center">

**fIPAR = min(-0.1336 × NDVI<sup>2</sup> + 1.4653 × NDVI + 0.1032, 0.95)**

</div>

#### Plant Temperature Constraint (f_T)

<div align="center">

**f<sub>T</sub> = exp(-((T<sub>a</sub> - T<sub>opt</sub>) / T<sub>opt</sub>)<sup>2</sup>)**

</div>

Where:
- **Ta** = Air temperature [°C]
- **Topt** = Optimum temperature for photosynthesis [°C], derived from global climatology

#### Plant Moisture Constraint (f_M)

<div align="center">

**f<sub>M</sub> = fAPAR / fAPAR<sub>max</sub>**

</div>

Where:
- **fAPARmax** = Maximum climatological fAPAR for each location

#### Soil Moisture Constraint (f_SM)

<div align="center">

**f<sub>SM</sub> = min(RH / (RH + VPD/β), 1.0)**

</div>

Where:
- **VPD** = Vapor pressure deficit [Pa]
- **β** = Empirical parameter (200 Pa) representing soil-atmosphere coupling

### Step-by-Step Methodology

#### Step 1: Vegetation Index Processing
1. Calculate SAVI from NDVI
2. Derive fAPAR and fIPAR from vegetation indices
3. Compute green canopy fraction (f_g)
4. Calculate LAI using Carlson method

#### Step 2: Energy Balance Components
1. Calculate net radiation using Verma method if not provided
2. Estimate soil heat flux using SEBAL approach if not provided
3. Partition net radiation between soil and canopy using LAI

#### Step 3: Meteorological Processing
1. Calculate saturation vapor pressure slope (Δ)
2. Compute energy partitioning coefficient (ε)
3. Derive vapor pressure deficit (VPD)
4. Calculate surface wetness (f_wet)

#### Step 4: Constraint Function Calculation
1. Plant temperature constraint (f_T) from Ta and Topt
2. Plant moisture constraint (f_M) from fAPAR and fAPARmax
3. Soil moisture constraint (f_SM) from RH and VPD

#### Step 5: Component ET Calculation
1. Soil evaporation with wetness and soil moisture constraints
2. Canopy transpiration with all biophysical constraints
3. Interception evaporation from wet surfaces
4. Sum components for total evapotranspiration

#### Step 6: Quality Control and Validation
1. Constrain individual components to physical limits
2. Ensure total LE ≤ potential ET (α × ε × (Rn - G))
3. Apply spatial and temporal consistency checks

### Remote Sensing Implementation

The PT-JPL model is specifically designed for satellite remote sensing applications:

**Required Inputs:**
- **NDVI** from optical sensors (Landsat, MODIS, ECOSTRESS)
- **Surface temperature** from thermal infrared sensors
- **Surface albedo** from broadband optical observations
- **Surface emissivity** from thermal infrared or vegetation indices

**Optional Automatic Retrievals:**
- **Air temperature** and **relative humidity** from GEOS-5 FP reanalysis
- **Net radiation** calculated using Verma method
- **Soil heat flux** estimated using SEBAL algorithm
- **fAPARmax** and **Topt** from global climatological datasets

### Model Validation and Performance

The PT-JPL model has been extensively validated against eddy covariance measurements:

- **Global validation:** 173 FLUXNET sites across diverse biomes
- **RMSE:** ~65 W m⁻² for instantaneous LE estimates
- **Correlation (r):** 0.85-0.92 depending on biome type
- **Bias:** Generally <10% across well-instrumented sites

**Performance characteristics:**
- **Best performance:** Croplands, grasslands, deciduous forests
- **Moderate performance:** Evergreen forests, shrublands
- **Challenges:** Very arid ecosystems, urban areas, snow-covered surfaces

### Advantages and Limitations

**Advantages over Classical Priestley-Taylor:**
- Accounts for vegetation water stress and phenology
- Provides component-level ET partitioning
- Utilizes readily available remote sensing data
- Suitable for heterogeneous landscapes
- Incorporates spatial variability in surface properties

**Limitations:**
- Requires quality remote sensing inputs
- More complex parameterization than classical PT
- Sensitive to atmospheric correction of satellite data
- May overestimate ET in extremely arid conditions
- Assumes energy limitation in well-watered pixels

**Advantages over Penman-Monteith:**
- Fewer meteorological input requirements
- More stable in data-sparse regions
- Better suited for remote sensing applications
- Computationally efficient for large-scale processing

## Usage

```python
import PTJPL

# Basic usage with required inputs
results = PTJPL.PTJPL(
    NDVI=ndvi_array,
    ST_C=surface_temperature,
    albedo=surface_albedo,
    emissivity=surface_emissivity,
    Ta_C=air_temperature,
    RH=relative_humidity,
    Rn_Wm2=net_radiation,
    G_Wm2=soil_heat_flux
)

# Access individual ET components
total_ET = results["LE_Wm2"]
soil_evaporation = results["LE_soil_Wm2"]
canopy_transpiration = results["LE_canopy_Wm2"] 
interception = results["LE_interception_Wm2"]

# Advanced usage with automatic data retrieval
from datetime import datetime
from rasters import RasterGeometry

geometry = RasterGeometry.from_bounds(...)
time_utc = datetime(2024, 6, 15, 12, 0)

results = PTJPL.PTJPL(
    NDVI=ndvi_raster,
    ST_C=surface_temp_raster,
    albedo=albedo_raster,
    emissivity=emissivity_raster,
    geometry=geometry,
    time_UTC=time_utc,
    upscale_to_daylight=True  # Calculate daily ET
)
```

## References

### Core PT-JPL Model Development
- **Fisher, J. B., Tu, K. P., & Baldocchi, D. D. (2008).** Global estimates of the land-atmosphere water flux based on monthly AVHRR and ISLSCP-II data, validated at 16 FLUXNET sites. *Remote Sensing of Environment*, 112(3), 901-919. https://doi.org/10.1016/j.rse.2007.06.025
  - *Original PT-JPL model formulation and global validation*

- **Fisher, J. B., Melton, F., Middleton, E., Hain, C., Anderson, M., Allen, R., ... & Wood, E. F. (2017).** The future of evapotranspiration: Global requirements for ecosystem functioning, carbon and climate feedbacks, agricultural management, and water resources. *Water Resources Research*, 53(4), 2618-2626. https://doi.org/10.1002/2016WR020175
  - *Comprehensive review of ET modeling requirements and PT-JPL applications*

- **Purdy, A. J., Fisher, J. B., Goulden, M. L., Colliander, A., Halverson, G., Tu, K., & Famiglietti, J. S. (2018).** SMAP soil moisture improves global evapotranspiration. *Remote Sensing of Environment*, 219, 1-14. https://doi.org/10.1016/j.rse.2018.09.023
  - *Enhanced PT-JPL with satellite soil moisture constraints*

### Foundational Priestley-Taylor Theory
- **Priestley, C. H. B., & Taylor, R. J. (1972).** On the assessment of surface heat flux and evaporation using large-scale parameters. *Monthly Weather Review*, 100(2), 81-92. https://doi.org/10.1175/1520-0493(1972)100<0081:OTAOSH>2.3.CO;2
  - *Original derivation and validation of the Priestley-Taylor equation*

- **Penman, H. L. (1948).** Natural evaporation from open water, bare soil and grass. *Proceedings of the Royal Society of London Series A*, 193(1032), 120-145. https://doi.org/10.1098/rspa.1948.0037
  - *Theoretical foundation for combination evapotranspiration equations*

### Remote Sensing and Energy Balance Methods
- **Verma, S. B., Rosenberg, N. J., & Blad, B. L. (1976).** Turbulent exchange coefficients for sensible heat and water vapor under advective conditions. *Journal of Applied Meteorology*, 15(4), 330-338. https://doi.org/10.1175/1520-0450(1976)015<0330:TECFSH>2.0.CO;2
  - *Net radiation calculation methodology used in PT-JPL*

- **Bastiaanssen, W. G. M., Menenti, M., Feddes, R. A., & Holtslag, A. A. M. (1998).** A remote sensing surface energy balance algorithm for land (SEBAL). 1. Formulation. *Journal of Hydrology*, 212-213, 198-212. https://doi.org/10.1016/S0022-1694(98)00253-4
  - *SEBAL algorithm for soil heat flux estimation*

- **Carlson, T. N., & Ripley, D. A. (1997).** On the relation between NDVI, fractional vegetation cover, and leaf area index. *Remote Sensing of Environment*, 62(3), 241-252. https://doi.org/10.1016/S0034-4257(97)00104-1
  - *Vegetation index relationships used in PT-JPL*

### ECOSTRESS Mission and Applications
- **Hook, S. J., Fisher, J. B., Schleyer, T., Schaepman, M. E., Huete, A., Cawse-Nicholson, K., ... & Green, R. O. (2019).** The ECOSTRESS mission. *IEEE Transactions on Geoscience and Remote Sensing*, 57(7), 4288-4301. https://doi.org/10.1109/TGRS.2019.2895618
  - *ECOSTRESS mission overview and PT-JPL operational implementation*

- **Hulley, G. C., Shivers, S., Wetherley, E., Cudd, R., Hook, S. J., Johnson, W. R., ... & Rivera, G. (2019).** New ECOSTRESS and MODIS Land Surface Temperature Data Reveal Fine-Scale Heat Vulnerability in Cities: A Case Study for Los Angeles County, California. *Remote Sensing*, 11(18), 2136. https://doi.org/10.3390/rs11182136
  - *High-resolution thermal remote sensing applications*

### Biophysical Parameterizations
- **Myneni, R. B., Hoffman, S., Knyazikhin, Y., Privette, J. L., Glassy, J., Tian, Y., ... & Running, S. W. (2002).** Global products of vegetation leaf area and fraction absorbed PAR from year one of MODIS data. *Remote Sensing of Environment*, 83(1-2), 214-231. https://doi.org/10.1016/S0034-4257(02)00074-3
  - *fAPAR retrieval algorithms and global datasets*

- **Huete, A. R. (1988).** A soil-adjusted vegetation index (SAVI). *Remote Sensing of Environment*, 25(3), 295-309. https://doi.org/10.1016/0034-4257(88)90106-X
  - *Soil-Adjusted Vegetation Index used in PT-JPL vegetation processing*

### Validation and Intercomparison Studies
- **Michel, D., Jiménez, C., Miralles, D. G., Jung, M., Hirschi, M., Ershadi, A., ... & Fernández-Prieto, D. (2016).** The WACMOS-ET project–Part 1: Tower-scale evaluation of four remote-sensing-based evapotranspiration algorithms. *Hydrology and Earth System Sciences*, 20(2), 803-822. https://doi.org/10.5194/hess-20-803-2016
  - *Multi-model ET algorithm intercomparison including PT-JPL*

- **Miralles, D. G., Jiménez, C., Jung, M., Michel, D., Ershadi, A., McCabe, M. F., ... & Fernández-Prieto, D. (2016).** The WACMOS-ET project–Part 2: Evaluation of global terrestrial evapotranspiration data sets. *Hydrology and Earth System Sciences*, 20(2), 823-842. https://doi.org/10.5194/hess-20-823-2016
  - *Global evaluation of ET products including PT-JPL*

### Methodological Standards
- **Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998).** Crop evapotranspiration: Guidelines for computing crop water requirements. *FAO Irrigation and Drainage Paper 56*. FAO, Rome. https://www.fao.org/3/x0490e/x0490e00.htm
  - *International standard for evapotranspiration calculations*

- **Monteith, J. L., & Unsworth, M. H. (2013).** Principles of Environmental Physics: Plants, Animals, and the Atmosphere. 4th Edition. Academic Press. ISBN: 978-0-12-386910-4
  - *Comprehensive treatment of environmental physics and energy balance principles*

### Vapor Pressure and Psychrometric Relationships
- **Magnus, G. (1844).** Versuche über die Spannkräfte des Wasserdampfs. *Annalen der Physik*, 137(12), 225-247. https://doi.org/10.1002/andp.18441371202
  - *Original formulation of vapor pressure-temperature relationships*

- **Murray, F. W. (1967).** On the computation of saturation vapor pressure. *Journal of Applied Meteorology*, 6(1), 203-204. https://doi.org/10.1175/1520-0450(1967)006<0203:OTCOSV>2.0.CO;2
  - *Accuracy assessment of Magnus-Tetens approximation used in psychrometric calculations*
