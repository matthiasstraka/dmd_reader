"""
Copyright DEWETRON GmbH 2024

Dmd reader library - Unit Tests
"""
import os
from dmd_reader import DmdReader

DMD = os.path.join(os.path.dirname(__file__), "../data", "oxy721.dmd")

def test_read_version():
    """
    Load a DMD file and check that the version info is read correctly
    """
    with DmdReader(DMD) as dmd:
        assert dmd.dmd_version.major == 8
        assert dmd.dmd_version.minor == 0
        assert str(dmd.dmd_version) == '8.0'
        assert dmd.dmd_library == 'DMD Library ver.2.3.0.0'
