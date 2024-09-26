"""
Contains commonly used types
"""

from dataclasses import dataclass

@dataclass
class Version:
    """Version information"""
    major: int
    minor: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

    def __repr__(self) -> str:
        return f"{self.major}.{self.minor}"
