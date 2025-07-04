from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status, Body, Depends
from fastapi.responses import JSONResponse
from models.schemas import (
    QuickClaimRequest, 
    QuickClaimResponse, 
    MedicalReportValidationResponse,
    FullClaimEvaluationResponse,
    ClaimResponse,
    CardiacEvent,
    UserSignup,
    UserLogin,
    UserOut
)
from services.gemini_service import GeminiService
from utils.mongo import db
from datetime import datetime
import hashlib

router = APIRouter(prefix="/api", tags=["claims"])
gemini_service = GeminiService()

@router.post("/signup", response_model=UserOut, status_code=201)
async def signup(user: UserSignup = Body(...)):
    # Hash the password (simple hash for demo; use bcrypt/argon2 in production)
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
    user_doc = {
        "email": user.email,
        "password": hashed_pw,
        "name": user.name
    }
    # Check if user exists
    existing = await db["users"].find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    result = await db["users"].insert_one(user_doc)
    return UserOut(user_id=str(result.inserted_id), email=user.email, name=user.name)

@router.post("/login")
async def login(user: UserLogin = Body(...)):
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
    user_doc = await db["users"].find_one({"email": user.email, "password": hashed_pw})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user_id": str(user_doc["_id"]), "email": user_doc["email"], "name": user_doc.get("name")}

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

@router.post("/calculate-claim", response_model=ClaimResponse)
async def calculate_claim(
    policy_file: UploadFile,
    sum_insured: float = Form(...),
    event_start: str = Form(...),
    event_end: str = Form(...),
    hospital_cost: float = Form(...)
):
    try:
        # Extract text from PDF
        policy_text = await gemini_service._extract_pdf_text(policy_file)

        # Prepare claim details
        claim_details = {
            "sum_insured": sum_insured,
            "event_start": event_start,
            "event_end": event_end,
            "hospital_cost": hospital_cost
        }

        # Generate claim analysis
        result = await gemini_service.generate_quick_claim(policy_file, sum_insured, event_start, event_end, hospital_cost)

        return ClaimResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cardiac-event", status_code=201)
async def add_cardiac_event(event: CardiacEvent = Body(...)):
    try:
        event_dict = event.dict(by_alias=True)
        # Ensure timestamp is in ISO format for MongoDB
        if isinstance(event_dict["timestamp"], datetime):
            event_dict["timestamp"] = event_dict["timestamp"].isoformat()
        result = await db["cardiac_events"].insert_one(event_dict)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"inserted_id": str(result.inserted_id)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 