"""Pydantic models for MedTriage-Env — Emergency Department Triage Environment."""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


class VitalsModel(BaseModel):
    """Patient vital signs."""
    heart_rate: int = Field(..., description="Heart rate in BPM (normal: 60-100)")
    bp_systolic: int = Field(..., description="Systolic blood pressure mmHg (normal: 90-140)")
    bp_diastolic: int = Field(..., description="Diastolic blood pressure mmHg (normal: 60-90)")
    spo2: int = Field(..., description="Oxygen saturation % (normal: 95-100)")
    temperature: float = Field(..., description="Body temperature °F (normal: 97.8-99.1)")
    respiratory_rate: int = Field(..., description="Breaths per minute (normal: 12-20)")


class PatientObservation(BaseModel):
    """Individual patient information visible to the agent."""
    patient_id: str
    chief_complaint: str
    vitals: VitalsModel
    age: int
    comorbidities: List[str] = []
    arrival_time: int = Field(..., description="Minutes since shift start")
    wait_minutes: int = Field(0, description="Minutes waiting since arrival")
    status: str = "waiting"
    tests_completed: List[str] = []
    consults_requested: List[str] = []
    assigned_esi: Optional[int] = None
    bed_id: Optional[str] = None


class EnvironmentObservation(BaseModel):
    """Full environment state visible to the agent."""
    current_time: int = Field(..., description="Minutes into the shift")
    bed_availability: int
    total_beds: int
    patients: List[PatientObservation]
    last_action_result: str = "Episode started."
    last_reward: float = 0.0
    episode_step: int = 0
    task_name: str
    done: bool = False


class TriageAction(BaseModel):
    """Action the agent can take."""
    action_type: Literal[
        "assign_priority",
        "order_test",
        "admit_to_bed",
        "consult",
        "discharge",
        "wait"
    ]
    patient_id: str = ""
    esi_level: Optional[int] = Field(None, ge=1, le=5)
    test_type: Optional[str] = Field(None)
    specialty: Optional[str] = Field(None)


class StepResponse(BaseModel):
    """Response from step() endpoint."""
    observation: EnvironmentObservation
    reward: float
    done: bool
    info: Dict[str, Any] = {}


class ResetRequest(BaseModel):
    """Request body for reset() endpoint."""
    task_name: str = "single_triage"
    seed: Optional[int] = None
