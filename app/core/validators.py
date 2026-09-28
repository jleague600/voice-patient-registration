import re

# All valid US state codes for checks.
VALID_US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}

# Name can have letters, spaces, hyphen, apostrophe.
NAME_PATTERN = re.compile(r"^[A-Za-z\-' ]{1,50}$")
ZIP_PATTERN = re.compile(r"^\d{5}(-\d{4})?$")


# Remove all non-digits and check that it is exactly 10 digits.
def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) != 10:
        raise ValueError("phone number must be a valid 10-digit US number")
    return digits


# Check if a name is valid.
def is_valid_name(value: str) -> bool:
    return bool(NAME_PATTERN.match(value))


# Check if state code is real US state.
def is_valid_us_state(value: str) -> bool:
    return value.upper() in VALID_US_STATES


# Check zip code format. Example: 12345 or 12345-6789.
def is_valid_zip(value: str) -> bool:
    return bool(ZIP_PATTERN.match(value))