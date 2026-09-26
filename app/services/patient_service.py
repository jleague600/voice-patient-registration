import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import normalize_phone
from app.models.patient import Patient
from app.models.schemas import PatientCreate, PatientUpdate


async def create_patient(db: AsyncSession, data: PatientCreate) -> Patient:
    """Insert a new patient record. Assumes `data` is already validated by Pydantic."""
    patient = Patient(**data.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


async def get_patient_by_id(db: AsyncSession, patient_id: uuid.UUID) -> Patient | None:
    """Fetch a single active (not soft-deleted) patient by ID."""
    result = await db.execute(
        select(Patient).where(Patient.patient_id == patient_id, Patient.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def find_patient_by_phone(db: AsyncSession, phone_number: str) -> Patient | None:
    """
    Look up an active patient by phone number. Used for the duplicate-
    detection bonus: the voice agent checks this before creating a new
    record, so a returning caller gets offered an update instead of a
    duplicate entry.
    """
    normalized = normalize_phone(phone_number)
    result = await db.execute(
        select(Patient).where(Patient.phone_number == normalized, Patient.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def list_patients(
    db: AsyncSession,
    last_name: str | None = None,
    date_of_birth=None,
    phone_number: str | None = None,
) -> list[Patient]:
    """
    List active patients, optionally filtered by the query params the
    spec requires: ?last_name=, ?date_of_birth=, ?phone_number=.
    Filters are combined with AND when more than one is given.
    """
    query = select(Patient).where(Patient.deleted_at.is_(None))

    if last_name:
        query = query.where(Patient.last_name.ilike(last_name))  # case-insensitive match
    if date_of_birth:
        query = query.where(Patient.date_of_birth == date_of_birth)
    if phone_number:
        query = query.where(Patient.phone_number == normalize_phone(phone_number))

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_patient(db: AsyncSession, patient_id: uuid.UUID, data: PatientUpdate) -> Patient | None:
    """
    Partial update -- only fields the caller actually provided are
    changed (model_dump(exclude_unset=True) is what makes this "partial"
    rather than overwriting everything with None).
    """
    patient = await get_patient_by_id(db, patient_id)
    if patient is None:
        return None

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(patient, field, value)

    await db.commit()
    await db.refresh(patient)
    return patient


async def soft_delete_patient(db: AsyncSession, patient_id: uuid.UUID) -> Patient | None:
    """Sets deleted_at instead of removing the row, per the spec's soft-delete requirement."""
    patient = await get_patient_by_id(db, patient_id)
    if patient is None:
        return None

    patient.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(patient)
    return patient