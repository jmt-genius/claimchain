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
    UserOut,
    FullClaimStatus
)
from services.gemini_service import GeminiService
from utils.mongo import db
from datetime import datetime
import hashlib
from bson import ObjectId
import os
from services.email_service import send_verification_link
from constants.insurance_text import policy_text
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
    user_id: str = Form(...),
    discharge_file: UploadFile = File(...),
    bill_file: UploadFile = File(...)
):
    """
    Evaluate a full insurance claim based on policy document, discharge summary, and medical bill.
    Also store claim details in MongoDB with status 'waiting'.
    Returns the claim's _id as claim_id in the response.
    """
    try:
        # Read file bytes for hashing
        discharge_bytes = await discharge_file.read()
        bill_bytes = await bill_file.read()
        discharge_hash = hashlib.sha256(discharge_bytes).hexdigest()
        bill_hash = hashlib.sha256(bill_bytes).hexdigest()

        # Store in MongoDB
        insert_result = await db["full_claims"].insert_one({
            "user_id": user_id,
            "discharge_hash": discharge_hash,
            "bill_hash": bill_hash,
            "status": FullClaimStatus.waiting.value,
            "created_at": datetime.utcnow()
        })
        claim_id = str(insert_result.inserted_id)

        # Rewind file pointers for Gemini if needed
        discharge_file.file.seek(0)
        bill_file.file.seek(0)

        result = await gemini_service.evaluate_full_claim(
            discharge_file=discharge_file,
            bill_file=bill_file
        )
        # Add claim_id to the response
        result["claim_id"] = claim_id
        return result
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
    body: dict = Body(...)
):
    try:
        user_id = body.get("user_id")
        if not user_id:
            raise HTTPException(status_code=422, detail="user_id is required in the request body.")
        # Fetch the latest cardiac event for the user
        event = await db["cardiac_events"].find_one({"customerId": user_id}, sort=[("timestamp", -1)])
        if not event:
            raise HTTPException(status_code=404, detail="No cardiac event found for this user.")
        event_start = event_end = event["timestamp"]
        bpm = event["bpm"]

        # Hardcoded values
        sum_insured = 1000000
        hospital_cost = 50000

        policy_text = policy_text
    # Prepare claim details
        claim_details = {
            "sum_insured": sum_insured,
            "event_start": event_start,
            "event_end": event_end,
            "hospital_cost": hospital_cost,
            "bpm": bpm
        }

        # Generate claim analysis
        result = gemini_service.generate_claim_analysis(policy_text, claim_details)

        return ClaimResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-hospital-verification-email/{claim_id}")
async def send_hospital_verification_email(claim_id: str, body: dict = Body(...)):
    email = body.get("email")
    # Hardcoded verification link
    link = f"https://yourdomain.com/hospital-verify?claim_id={claim_id}"
    if not email:
        raise HTTPException(status_code=422, detail="'email' is required.")
    try:
        # Fetch claim and user for personalization
        claim = await db["full_claims"].find_one({"_id": ObjectId(claim_id)})
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found.")
        user = await db["users"].find_one({"_id": ObjectId(claim["user_id"])})
        patient_name = user.get("name") if user else None
        # Personalised message
        if patient_name:
            message = f"Dear Hospital,\n\nA claim verification is requested for patient: {patient_name}. Please upload the required documents using the following link: {link}\n\nThank you."
        else:
            message = f"Dear Hospital,\n\nA claim verification is requested. Please upload the required documents using the following link: {link}\n\nThank you."
        await send_verification_link(email, link, message=message)
        return {"success": True, "message": f"Verification link sent to {email}", "claim_id": claim_id, "link": link}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.post("/verify-hospital-upload/{claim_id}")
async def verify_hospital_upload(claim_id: str, discharge_file: UploadFile = File(...), bill_file: UploadFile = File(...)):
    try:
        # Read and hash the uploaded files
        discharge_bytes = await discharge_file.read()
        bill_bytes = await bill_file.read()
        discharge_hash = hashlib.sha256(discharge_bytes).hexdigest()
        bill_hash = hashlib.sha256(bill_bytes).hexdigest()

        # Find the matching full claim in DB by claim_id
        claim = await db["full_claims"].find_one({
            "_id": ObjectId(claim_id),
            "discharge_hash": discharge_hash,
            "bill_hash": bill_hash,
            "status": "waiting"
        })
        if not claim:
            return {"success": False, "reason": "No matching claim found or already approved."}

        # Update status to approved
        await db["full_claims"].update_one(
            {"_id": claim["_id"]},
            {"$set": {"status": "approved", "approved_at": datetime.utcnow()}}
        )
        return {"success": True, "message": "Claim verified and approved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@router.get("/claim-status/{claim_id}")
async def claim_status(claim_id: str):
    claim = await db["full_claims"].find_one({"_id": ObjectId(claim_id)})
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found.")
    return {
        "claim_id": claim_id,
        "status": claim.get("status"),
        "created_at": claim.get("created_at"),
        "approved_at": claim.get("approved_at")
    }