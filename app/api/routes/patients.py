import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.logging import log_event
from app.models.schemas import APIResponse, PatientCreate, PatientOut, PatientUpdate
from app.services import patient_service

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=APIResponse)
async def list_patients(
    last_name: str | None = Query(None),
    date_of_birth: date | None = Query(None),
    phone_number: str | None = Query(None),
    db: AsyncSession = Depends(get_session),
):
    patients = await patient_service.list_patients(
        db, last_name=last_name, date_of_birth=date_of_birth, phone_number=phone_number
    )
    return APIResponse(data=[PatientOut.model_validate(p) for p in patients])


@router.get("/{patient_id}", response_model=APIResponse)
async def get_patient(patient_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    patient = await patient_service.get_patient_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return APIResponse(data=PatientOut.model_validate(patient))


@router.post("", response_model=APIResponse, status_code=201)
async def create_patient(data: PatientCreate, db: AsyncSession = Depends(get_session)):
    try:
        patient = await patient_service.create_patient(db, data)
    except Exception as e:
        # Catches DB-level failures (e.g. constraint violations) so the
        # caller gets a clean error instead of a raw 500 with a stack trace.
        raise HTTPException(status_code=500, detail=f"Failed to create patient: {str(e)}")

    log_event("patient_created", {"patient_id": str(patient.patient_id), "phone_number": patient.phone_number})
    return APIResponse(data=PatientOut.model_validate(patient))


@router.put("/{patient_id}", response_model=APIResponse)
async def update_patient(patient_id: uuid.UUID, data: PatientUpdate, db: AsyncSession = Depends(get_session)):
    patient = await patient_service.update_patient(db, patient_id, data)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    log_event("patient_updated", {"patient_id": str(patient_id)})
    return APIResponse(data=PatientOut.model_validate(patient))


@router.delete("/{patient_id}", response_model=APIResponse)
async def delete_patient(patient_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    patient = await patient_service.soft_delete_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    log_event("patient_deleted", {"patient_id": str(patient_id)})
    return APIResponse(data={"message": "Patient soft-deleted", "patient_id": str(patient_id)})