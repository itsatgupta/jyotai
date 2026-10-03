"""External location lookup boundary; never used by astrology calculations."""

from astrologer.locations.service import GeoapifyLocationService, LocationLookupError

__all__ = ["GeoapifyLocationService", "LocationLookupError"]
