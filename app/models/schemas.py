import uuid
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.core.validators import is_valid_name, is_valid_us_state, is_valid_zip, normalize_phone

VALID_SEX_VALUES = {"Male", "Female", "Other", "Decline to Answer"}


class PatientBase(BaseModel):
    """Shared fields/validation used by both create and update schemas."""

    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    sex: str
    phone_number: str
    email: EmailStr | None = None
    address_line_1: str = Field(..., min_length=1)
    address_line_2: str | None = None
    city: str = Field(..., min_length=1, max_length=100)
    state: str
    zip_code: str
    insurance_provider: str | None = None
    insurance_member_id: str | None = None
    preferred_language: str = "English"
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not is_valid_name(v):
            raise ValueError("must be 1-50 alphabetic characters, hyphens, or apostrophes only")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return v

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, v: str) -> str:
        if v not in VALID_SEX_VALUES:
            raise ValueError(f"sex must be one of {VALID_SEX_VALUES}")
        return v

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return normalize_phone(v)

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        if not is_valid_us_state(v):
            raise ValueError("state must be a valid 2-letter US state abbreviation")
        return v.upper()

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v: str) -> str:
        if not is_valid_zip(v):
            raise ValueError("zip_code must be 5 digits or ZIP+4 format (e.g. 12345 or 12345-6789)")
        return v


class PatientCreate(PatientBase):
    """Shape required for POST /patients -- all required fields must be present."""
    pass


class PatientUpdate(BaseModel):
    """
    Shape for PUT /patients/:id -- every field optional, since partial
    updates are allowed. Re-declares validators (rather than inheriting
    PatientBase) since nothing here is required.
    """

    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    date_of_birth: date | None = None
    sex: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = Field(None, min_length=1, max_length=100)
    state: str | None = None
    zip_code: str | None = None
    insurance_provider: str | None = None
    insurance_member_id: str | None = None
    preferred_language: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None and not is_valid_name(v):
            raise ValueError("must be 1-50 alphabetic characters, hyphens, or apostrophes only")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_not_future(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return v

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_SEX_VALUES:
            raise ValueError(f"sex must be one of {VALID_SEX_VALUES}")
        return v

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return normalize_phone(v)

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not is_valid_us_state(v):
            raise ValueError("state must be a valid 2-letter US state abbreviation")
        return v.upper()

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v: str | None) -> str | None:
        if v is not None and not is_valid_zip(v):
            raise ValueError("zip_code must be 5 digits or ZIP+4 format (e.g. 12345 or 12345-6789)")
        return v


class PatientLookup(BaseModel):
    """Request body for POST /patients/lookup (used by the voice agent's duplicate check)."""

    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_phone(v)

class PatientOut(PatientBase):
    """Shape returned to clients -- includes auto-generated fields."""

    patient_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # lets this be built directly from a Patient ORM object


class APIResponse(BaseModel):
    """Consistent response envelope required by the spec: { "data": ..., "error": null }"""

    data: PatientOut | list[PatientOut] | dict | None = None
    error: str | None = None