import pytest

# List of dependencies
dependencies = [
    "ECOv002_CMR",
    "ECOv002_granules",
    "GEOS5FP",
    "numpy",
    "pandas",
    "rasters",
    "verma_net_radiation"
]

# Generate individual test functions for each dependency
@pytest.mark.parametrize("dependency", dependencies)
def test_dependency_import(dependency):
    __import__(dependency)
