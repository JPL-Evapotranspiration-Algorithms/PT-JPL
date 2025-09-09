import pytest
from PTJPL import verify

def test_verify():
    assert verify(), "Model verification failed: outputs do not match expected results."
