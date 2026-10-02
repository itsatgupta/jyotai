"""Services that transform validated birth details into canonical input."""

from astrologer.birth.models import BirthDetails, BirthInput


class BirthInputNormalizer:
    """Create canonical birth input without performing astrology calculations."""

    def normalize(self, birth_details: BirthDetails) -> BirthInput:
        """Return a validated object with unambiguous local and UTC timestamps."""
        return BirthInput.model_validate(birth_details.model_dump())
