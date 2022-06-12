"""
An API wrapper for Parcoursup.
This whole package is licensed under the MPL2.0 license
"""

__title__ = "parcoursupy"
__author__ = "Bapt5"
__license__ = "MPL2.0"
__version__ = "1.0.0"

from .parcoursupAPI import (
    Parcoursup_Client,
    _Wish,
    Proposition,
    PendingWish,
    RefusedWish,
)
