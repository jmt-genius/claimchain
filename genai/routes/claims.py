from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from models.schemas import (
    QuickClaimRequest, 
    QuickClaimResponse, 
    MedicalReportValidationResponse,
    FullClaimEvaluationResponse
)
from services.gemini_service import GeminiService

router = APIRouter(prefix="/claims", tags=["claims"])
gemini_service = GeminiService()

@router.post("/evaluate-full-claim", response_model=FullClaimEvaluationResponse)
async def evaluate_full_claim(
    policy_file: UploadFile = File(...),
    discharge_file: UploadFile = File(...),
    bill_file: UploadFile = File(...)
):
    """
    Evaluate a full insurance claim based on policy document, discharge summary, and medical bill.
    
    - **policy_file**: PDF file containing the insurance policy
    - **discharge_file**: PDF file containing the discharge summary
    - **bill_file**: PDF file containing the medical bill
    
    Returns:
    - claimable_amount: The total amount that can be claimed
    - reasoning: Detailed explanation of what is covered and why
    - timestamp: When the evaluation was performed
    """
    try:
        result = await gemini_service.evaluate_full_claim(
            policy_file=policy_file,
            discharge_file=discharge_file,
            bill_file=bill_file
        )
        return FullClaimEvaluationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-medical-report", response_model=MedicalReportValidationResponse)
async def validate_medical_report(
    file: UploadFile = File(...)
):
    """
    Validate if the uploaded file is a valid medical report or discharge summary.
    
    - **file**: PDF file containing the potential medical report
    
    Returns:
    - is_valid_report: boolean indicating if it's a valid medical report
    - reason: explanation of the validation result
    - timestamp: when the validation was performed
    """
    try:
        result = await gemini_service.validate_medical_report(file=file)
        return MedicalReportValidationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick-claim", response_model=QuickClaimResponse)
async def generate_quick_claim(
    file: UploadFile = File(...),
    sum_insured: float = Form(...),
    event_start: str = Form(...),
    event_end: str = Form(...),
    hospital_cost: float = Form(...)
):
    """
    Generate a quick claim assessment for a cardiac event based on the policy document.
    Returns the claimable amount and quick claim amount (40% of claimable amount).
    
    - **file**: PDF file containing the insurance policy
    - **sum_insured**: Total sum insured amount
    - **event_start**: Start time of the cardiac event
    - **event_end**: End time of the cardiac event
    - **hospital_cost**: Average treatment cost
    """
    try:
        result = await gemini_service.generate_quick_claim(
            file=file,
            sum_insured=sum_insured,
            event_start=event_start,
            event_end=event_end,
            hospital_cost=hospital_cost
        )
        return QuickClaimResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 