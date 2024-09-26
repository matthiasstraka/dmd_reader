"""
This example opens a DMD file and reads its content
"""
from dmd_reader import DmdReader

FILENAME = 'data/oxy721.dmd'

print(f"Loading DMD file {FILENAME}...")
with DmdReader(FILENAME) as dmd:
    print(f"Loaded DMD version {dmd.dmd_version}")
