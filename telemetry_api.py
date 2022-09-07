"""Public API that tries to import C++ module, but falls back to Python."""

__all__ = (
    'SGP4_ERRORS', 'Satrec', 'SatrecArray', 'WGS72OLD', 'WGS72', 'WGS84',
    'accelerated', 'jday', 'days2mdhms',
)

from telemetry_functions import jday, days2mdhms

SGP4_ERRORS = {
    1: 'mean eccentricity is outside the range 0.0 to 1.0',
    2: 'nm is less than zero',
    3: 'perturbed eccentricity is outside the range 0.0 to 1.0',
    4: 'semilatus rectum is less than zero',
    5: '(error 5 no longer in use; it meant the satellite was underground)',
    6: 'mrt is less than 1.0 which indicates the satellite has decayed',
}

from telemetry_model import Satrec, SatrecArray
from telemetry_model import WGS72OLD, WGS72, WGS84
accelerated = False