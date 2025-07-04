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
from bson import ObjectId
import os

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

        policy_text = """ 
SBI General Insurance Company Limited                                   
                                                       
 
 
SBI General Insurance Company Limited Health Insurance Policy- Retail                     UIN: SBIHLIP21331V032021                  Page 1 of 45  
CUSTOMER INFORMATION SHEET 
 
(Description is illustrative and not exhaustive) 
 
S. No TITLE  DESCRIPTION REFER TO POLICY 
CLAUSE NUMBER 
1 Product 
Name 
Health Insurance Policy - Retail   
2 What am  I 
covered for 
Following  are covered as basic cover up to the limit specified in the 
policy schedule 
Scope of Cover 
1. Room, Board & Nursing expenses 
2. Medical Practitioner, Surgeon, Anesthetist, Consultants, and 
Specialists Fees 
3. Anesthesia, Blood, Oxygen, Operation Theatre Expenses, Surgical 
Appliances, Medicines & consumables, Diagnostic expenses and X
ray, Dialysis, Chemotherapy, Radiotherapy, Cost of Pacemaker, 
prosthesis/ internal implants and any medical Expenses incurred 
which is integral part of the operation 
4. Cataract Treatment 
5. Pre-Hospitalisation Expenses 
6. Post-Hospitalisation Expenses. 
7. Day Care Expenses. 
8. Ambulance Expenses 
9. Ayurvedic Medicine. 
10. Homeopathic and Unani system of medicine. 
11. Domiciliary Hospitalisation  
12. Organ Donor  
13. Free medical check-up  
14. Parental Care  
15. Accidental Hospitalisation  
16. Child Care  
17. Co-pay  
18. Convalescence Benefit  
19. HIV/AIDS Cover upto the Limit Rs.50,000  
20. Mental Illness Cover upto the Limit Rs.50,000  
21. Genetic Disorders upto the Limit Rs.50,000  
22. Internal Congenital Diseases covered upto the Limit Rs. 10% of Sum 
Insured. 
 
23. 12 Advance procedure upto 50% of Sum Insured  
Add on covers (available on payment of additional premium):  
1. Removal of Room & ICU rent sub-limits  
2. Removal of sub-limits on operation and consultancy charges  
3. Removal of Ayurvedic and homeopathic cover  
Note: Insurer’s Liability in respect of all claims admitted during the period 
of insurance shall not exceed the Sum Insured for the Insured person as 
mentioned in the schedule. 
  
 
SBI General Insurance Company Limited                                   
                                                       
 
 
SBI General Insurance Company Limited Health Insurance Policy- Retail                     UIN: SBIHLIP21331V032021                  Page 2 of 45  
3 What are the 
major 
Exclusions in 
the policy 
Following is a partial list of the policy exclusions. Please refer to the 
policy document for the complete list of exclusions: 
 
Exclusions 
1. Admission primarily for investigation & evaluation 
2. Admission primarily for rest Cure, rehabilitation and respite care 
3. Expenses related to the surgical treatment of obesity that do not 
fulfill certain conditions 
4. Change-of-Gender treatments 
5. Expenses for cosmetic or plastic surgery 
6. Expenses related to any treatment necessitated due to participation 
in hazardous or adventure sports 
(Note: the above is a partial listing of the policy exclusions. Please refer 
to the policy clauses for the full listing).   
4 Waiting 
period 
1. Initial waiting period: 30 days for all illnesses (not applicable on 
renewal or for accidents) 
Exclusions 
2. 90 days waiting period for some diseases and surgeries. 
3. 1 year for some diseases and surgeries. 
4. 2 years for some diseases and surgeries. 
5. 3 years for joint replacement due to degenerative condition (not 
applicable for accidents) 
6. Pre-existing diseases: Covered after 48 months unless otherwise 
provided 
5 Payout basis Indemnity basis for covered expenses up to specified sum insured.  Scope of Cover 
6 Cost sharing In case of a claim, this policy requires you to share the following costs: Scope of Cover 
10% of each claim as co-payment in case of non network hospitalisation 
7 Renewal 
Conditions 
The policy shall ordinarily be renewable except on misrepresentation by 
the insured person. grounds of fraud, 
i. The Company shall endeavor to give notice for renewal. 
However, the Company is not under obligation to give any 
notice for renewal. 
ii. Renewal shall not be denied on the ground that the insured 
person had made a claim or claims in the preceding policy 
years. 
iii. Request for renewal along with requisite premium shall be 
received by the Company before the end of the policy 
period. 
iv.  At the end of the policy period, the policy shall terminate 
and can be renewed within the Grace Period of 30 days  to 
maintain continuity of benefits without break in policy. 
Coverage is not available during the grace period. 
v.  No loading shall apply on renewals based on individual 
claims experience 
 
General 
Conditions  
8 Renewal 
Benefits 
Free Medical Checkup for 4 continuous claim free years  
9 Cancellation Cancellation: General 
 
SBI General Insurance Company Limited                                   
                                                       
 
 
SBI General Insurance Company Limited Health Insurance Policy- Retail                     UIN: SBIHLIP21331V032021                  Page 3 of 45  
i. The policyholder may cancel this policy by giving 1Sdays'written 
notice and in such an event, the Company shall refund premium for 
the unexpired policy period as detailed below. 
Period on risk Rate of premium refunded 
Up to one month 75% of annual rate 
Up to three months 50%of annual rate 
Up to six months 25% of annual rate 
Exceeding six 
months 
Nil 
 
 
Notwithstanding anything contained herein or otherwise, no 
refunds of premium shall be made in respect of Cancellation where, 
any claim has been admitted or has been lodged or any benefit has 
been availed by the insured person under the policy. 
 
ii. The Company may cancel the policy at any time on grounds of 
misrepresentation non-disclosure of material facts, fraud by the 
insured person by giving 15 days' written notice. There would be no 
refund of premium on cancellation on grounds or misrepresentation, 
non-disclosure of material facts or fraud. 
 
 
Conditions  
10 Claims a. For Cashless Service: 
Refer link for Hospital Network details – 
http://www.sbigeneral.in/portal/contact-us/hospital 
b. For Reimbursement of Claim: For reimbursement 
of claims the insured 
prescribed time limit as specified hereunder. 
Sl 
N
 o 
Type of Claim Prescribed Time limit 
1 Reimbursement of 
hospitalization, day care and 
pre-hospitalization expenses 
Within fifteen days of date 
of discharge from hospital 
2 Reimbursement of post 
hospitalization expenses 
Within fifteen days from 
completion of post 
hospitalization treatment 
For details on claim procedure please refer the policy document. 
General 
Conditions 
11 Policy 
Servicing 
 
If You/Insured Person may have a grievance that requires to be 
redressed, You/Insured Person may contact Us with the details of 
the grievance through: 
 
 
SBI General Insurance Company Limited                                   
                                                       
 
 
SBI General Insurance Company Limited Health Insurance Policy- Retail                     UIN: SBIHLIP21331V032021                  Page 4 of 45  
• Level 1 
Call us on our Toll Free for any queries that you may have @ 
1800221111, 18001021111 
Email your queries to customer.care@sbigeneral.in 
Visit our website www.sbigeneral.in to register for your queries 
Please walk into any of our branch office or corporate office 
during business hours 
You may also fax us your queries at _1800227244, 18001027244 
• Level 2  
If you still are not happy about the resolution provided then you 
may please write to our head.customercare@sbigeneral.in 
• Level 3 
If you are dissatisfied with the resolution provided in the Steps 
as indicated above on your Complaint, you may send your 
‘Appeal’ addressed to the Chairman of the Grievance Redressal 
Committee. The Committee will look into the appeal and decide 
the same expeditiously on merits. 
You can write to Head – Compliance, Legal & CS on the id - 
gro@sbigeneral.in 
 
• Level 4 
If your issue remains unresolved you may approach IRDA by calling 
on the Toll Free no. 155255 or you can register an online complaint 
on the 
website http://igms.irda.gov.in 
• Senior Citizens: Senior Citizens can also write to 
seniorcitizengrievances@sbigeneral.in 
If after having followed the above steps you are not happy with the 
resolution and your issue remains unresolved, you may approach the 
Insurance Ombudsman for Redressal. 
12 Grievances/ 
Complaints 
a. Details of Grievance redressal officer - 
https://www.sbigeneral.in/portal/grievance-redressal 
b. IRDAI Integrated Grievance Management System - 
https://igms.irda.gov.in/ 
Insurance Ombudsman — The contact details of the Insurance 
Ombudsman offices have been provided as Annexure-B of Policy 
document 
General 
Conditions 
13 Insured's 
Rights 
1. Free Look period of 15 days from the date of receipt of the 
policy shall be applicable at the inception. 
2. Right to migrate from one product to another product of the 
company 
General 
Conditions 
 
SBI General Insurance Company Limited                                   
                                                       
 
 
SBI General Insurance Company Limited Health Insurance Policy- Retail                     UIN: SBIHLIP21331V032021                  Page 5 of 45  
For Queries related to migration contact below:- 
  Toll free no. – 1800-22-1111 
Email Id- Customer.care@sbigeneral.in  
3. Right to port the from one company to another company. 
For Queries related to portability contact below:- 
  Toll free no. – 1800-22-1111 
Email Id- Customer.care@sbigeneral.in 
 
14 Insured's 
Obligations 
Please disclose all pre-existing disease/s or condition/s before 
buying a policy. Non-disclosure may result in claim not being paid. 
 
 
 
Benefit Illustration: 
 
 
 
(LEGAL DISCLAIMER) NOTE: The information must be read in conjunction with the product brochure and policy 
do1cument. In case of any conflict between the Customer Information Sheet and the policy document the terms and 
conditions mentioned in the policy document shall prevail. 
  
Age of
 the
 members
 insured
 Premiu
 m (Rs.)
 Sum
 Insured
 (Rs.)
 Premi
 um
 (Rs.)
 Discou
 nt, if
 any
 Family
 memb
 er
 discou
 nt)
 Premi
 um
 after
 Discou
 nt (Rs.)
 Sum
 Insured
 (Rs.)
 Premi
 um or
 consoli
 dated
 premi
 um for
 all
 memb
 ers of
 family
 (Rs.)
 Floater
 discou
 nt if
 any
 Premi
 um
 after
 discou
 nt
 (Rs.)
 Sum
 Insured
 (Rs.)
 35 yrs 5,97355,00,000 5,973 0% 5,97355,00,000
 30 yrs 5,97355,00,000 5,973 0% 5,97355,00,000
 15 yrs NA NA 5,027 0% 5,02755,00,000
 10 yrs NA NA 5,027 0% 5,02755,00,000
 Total Premium for all members
 of the Family is Rs. 11,946/
when each member is covered
 separately.
 Sum Insured available for each
 individual is Rs.5,00,000/
Total Premium for all members of
 the Family is Rs. 22,000/- when they
 are covered under a single policy.
 Sum Insured available for each
 family member is Rs. 5,00,000/
Total Premium when policy is opted
 on floater basis is Rs. 14,933/
Sum Insured of Rs. 5,00,000/- is
 available for the entire family.
 Note:
 considering any loading. Also, the premium rates are exclusive of taxes applicable.
 Health Insurance policy Retail
 Coverage opted on
 individual basis
 covering each
 member of the
 family separately
 (at a single point in
 time)
 Coverage opted on individual basis
 covering multiple members of the
 family under a single policy (Sum
 Insured is available for each member
 of the family)
 Coverage opted on family floater
 basis with overall Sum Insured (Only
 one Sum Insured is available for the
 entire family)
 14,933 0% 14,933 5,00,000
SBI General Insurance Company Limited                                   
HEALTH INSURANCE POLICY –RETAIL  
This Policy is issued to the Insured based on the Proposal and declaration together with any statement, report or 
other document which shall be the basis of this contract and shall be deemed to be incorporated herein, to Insurer 
upon payment of the Premium.  This Policy records the agreement between Insurer and Insured and sets out the 
terms of insurance and the obligations of each party. 
The Policy, the Schedule and any Endorsement shall be read together and any word or expression to which a specific 
meaning has been attached in any part of this Policy or of Schedule shall bear such meaning whenever it may appear. 
Subject to the terms, Conditions, exclusions and definitions contained herein or endorsed or otherwise expressed 
hereon, Insurer undertakes to pay the Insured Person the hospitalization expenses arising out of an Injury or 
Illness/Disease and that are reasonably and necessarily incurred by or on behalf of such Insured Person, but not 
exceeding the sum Insured for the insured person as mentioned in the schedule of the policy. The following benefits 
are covered under this policy subject to the sub-limits as stipulated in the policy contract. 
1. Room, Boarding Expenses  
2. Medical Practitioners fees(Including Teleconsultation) 
3. Intensive Care Unit 
4. Nursing Expenses 
5. Surgical fees, operating theatre, Anesthetist, Anesthesia, Blood, Oxygen and their administration,  
6. Physio therapy while being treated as inpatient and being part of the treatment. 
7. Drugs and medicines consumed during hospitalization period. 
8. Hospital miscellaneous services (such as laboratory, X-ray, diagnostic tests) 
9. Dressing, ordinary splints and plaster casts. 
10. Cost of Prosthetic devices if implanted during a surgical procedure. 
Note: Insurer’s Liability in respect of all claims admitted during the period of insurance shall not exceed the Sum 
Insured for the Insured person as mentioned in the schedule. 
DEFINITIONS 
The following words or terms shall have the meaning ascribed to them wherever they appear in this Policy, and 
references to the singular or to the masculine shall include references to the plural and to the feminine wherever the 
context so permits: 
"Accident" means a sudden, unforeseen and involuntary event caused by external, visible and violent means. 
“Administrator” means any third party administrator engaged by the Insurer for providing Policy and claims 
facilitation services to the Insured as well as to the Insurer and who is duly licensed by IRDA for the said purpose. 
“Age” means completed years as at the Commencement Date of the Policy Period. 
“Alternative treatments” mean forms of treatments other than treatment "Allopathy" or "modem medicine" and 
includes Ayurveda, Unani, Sidha and Homeopathy in the Indian context. 
UIN: SBIHLIP21331V032021                  
Page 6 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
“Any One Illness” means continuous period of illness and it includes relapse within 45 days from the date of last 
consultation with the Hospital/Nursing Home where treatment may have been taken. 
Associated Medical Expenses shall include Room Rent, nursing charges, operation theatre charges, fees of Medical 
Practitioner/surgeon/ anaesthetist/ Specialist conducted within the same Hospital where the Insured Person has been 
admitted. The below expenses are not part of associate medical expenses 
a. Cost of Pharmacy and consumables 
b. Cost of implants and medical devices 
c. 
Cost of diagnostics 
An AYUSH Hospital is a healthcare facility wherein medical/surgical/para-surgical treatment 
procedures and interventions are carried out by AYUSH Medical Practitioner(s) comprising of any of the following. 
a) Central or State Government AYUSH Hospital or 
b) Teaching hospital attached to AYUSH College recognized by the Central Government/Central Council of 
Indian Medicine/Central Council for Homeopathy; 
Or  
c) AYUSH Hospital, standalone or co-located with in-patient healthcare facility of any recognized system of 
medicine, registered with the local authorities, wherever applicable, and is under the supervision of a 
qualified registered AYUSH Medical Practitioner and must comply with all the following criterion: 
i. 
ii. 
iii. 
iv. 
Having at least 5 in-patient beds; 
Having qualified AYUSH Medical Practitioner in charge round the clocks; 
Having dedicated AYUSH therapy sections as required and/or has equipped operation theatre 
where surgical procedures are to be carried out, 
Maintaining daily records of the patients and making them accessible to the insurance 
company's authorized representative. 
AYUSH Day Care Centre means and includes Community Health Centre (CHC), Primary 
Health Centre (PHC), Dispensary, Clinic, Polyclinic or any such health centre which is registered with the local 
authorities, wherever applicable and having facilities for carrying out treatment procedures and medical or 
surgical/para-surgical interventions or both under the supervision of registered AYUSH Medical Practitioner (s) 
on day care basis without in-patient services and must comply with all the following criterion: 
i. 
ii. 
Having qualified registered AYUSH Medical Practitioner(s) in charge; 
Having dedicated AYUSH therapy sections as required and/or has 
equipped operation theatre where surgical procedures are to be carried 
out; 
Maintaining daily records of the patients and making them accessible 
to the insurance company’s authorized representative. 
“Cashless facility” means a facility extended by the insurer to the insured where the payments, of the costs of 
treatment undergone by the insured in accordance with the policy terms and conditions, are directly made to the 
network provider by the insurer to the extent pre-authorization approved. 
UIN: SBIHLIP21331V032021                  
Page 7 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
“Co-payment” means a cost-sharing requirement under a health insurance policy that provides that the 
policyholder/insured will bear a specified percentage of the admissible claim amount. A co-payment does not reduce 
the Sum Insured. 
“Congenital Anomaly” refers to a condition(s) which is present since birth, and which is abnormal with reference to 
form, structure or position. 
a. 
b. 
Internal Congenital Anomaly – Congenital anomaly which is not in the visible and accessible parts of the body. 
External Congenital Anomaly - Congenital anomaly which is in the visible and accessible parts of the body.  
“Condition Precedent” means a policy term or condition upon which the Insurer's liability under the policy is 
conditional upon. 
“Cumulative Bonus” means any increase in the Sum Insured granted by the insurer without an associated increase in 
premium. 
“Day Care Expenses” means the Reasonable and Customary Charges incurred towards medical treatment for a Day 
Care Treatment /Procedure preauthorized by the Administrator and done in a Network Provider / Day Care Centre to 
the extent that such cost does not exceed the Reasonable and Customary charges in the locality for the same Day 
Care Treatment / Procedure. 
“Day Care Hospital/Centre” means any institution established for day care treatment of illness and / or injuries or a 
medical setup within a hospital and which has been registered with the local authorities, wherever applicable, and is 
under the supervision of a registered and qualified medical practitioner AND must comply with all minimum criteria 
as under 
a. 
b. 
c. 
d. 
has qualified nursing staff under its employment  
has qualified medical practitioner (s) in charge  
has a fully equipped operation theatre of its own where surgical procedures are carried out 
maintains daily records of patients and will make these accessible to the insurance company’s authorized 
personnel.  
“Day care Treatments” refers to medical treatment, and/or surgical procedure which is: 
a. 
undertaken under General or Local Anaesthesia in a Hospital/day care centre in less than 24 hrs because of 
technological advancement, and 
b. 
which would have otherwise required a Hospitalisation of more than 24 hours.  
Treatment normally taken on an out-patient basis is not included in the scope of this definition. 
“Deductible” means a cost-sharing requirement under a health insurance policy that provides that the Insurer will not 
be liable for a specified rupee amount in case of  indemnity policies and for a specified number of days/hours in case 
of hospital cash policies, which will apply before any benefits are payable by the insurer. A deductible does not reduce 
the sum insured. 
“Diagnostic Centre” means the diagnostic centers which have been empanelled by Insurer or Administrator as per 
the latest version of the Schedule of diagnostic centers maintained by Insurer or Administrator, which is available to 
Insured on request. 
UIN: SBIHLIP21331V032021                  
Page 8 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
“Disclosure to information norm” The Policy shall be void and all premium paid hereon shall be forfeited to the 
Company, in the event of misrepresentation, mis-description or non-disclosure of any material fact. 
“Dental treatment” means treatment carried out by a dental practitioner including examinations, fillings (where 
appropriate), crowns, extractions and surgery excluding any form of cosmetic surgery/implants. 
“Dependent Child/Children” means children / a child (natural or legally adopted), who are/is financially dependent 
on the Insured or Proposer aged between 3 months and twenty three (23) years and who are unmarried   
“Disease / Illness” means a sickness or a disease or pathological condition leading to the impairment of normal 
physiological function which manifests itself during the Policy Period and requires medical treatment. 
a. 
Acute condition - Acute condition is a disease, illness or injury that is likely to respond quickly to treatment 
which aims to return the person to his or her state of health immediately before suffering the 
disease/illness/injury which leads to full recovery. 
b. 
Chronic condition - A chronic condition is defined as a disease, illness, or injury that has one or more of the 
following characteristics 
i. 
ii. 
iii. 
iv. 
v. 
it needs ongoing or long-term monitoring through consultations, examinations, check-ups, and / or 
tests 
it needs ongoing or long-term control or relief of symptoms 
it requires your rehabilitation or for you to be specially trained to cope with it 
it continues indefinitely 
it comes back or is likely to come back. 
“Domiciliary Hospitalisation” means medical treatment for an illness/disease/injury which in the normal course 
would require care and treatment at a hospital but is actually taken while confined at home under any of the 
following circumstances: 
a. 
b. 
the condition of the patient is such that he/she is not in a condition to be removed to a hospital, or 
the patient takes treatment at home on account of non availability of room in a hospital. 
“Eligible Hospitalisation Expenses” means the expenses which the Insured/Insured Person is entitled for applicable 
room rent and other charges as given in the scope of cover under the policy. 
“Emergency Care” means management for a severe illness or injury which results in symptoms which occur suddenly 
and unexpectedly, and requires immediate care by a medical practitioner to prevent death or serious long term 
impairment of the insured person’s health. 
“Epidemic Disease” means a Disease which occurs when new cases of a certain Disease, in a given human population, 
and during a given period, substantially exceed what is the normal "expected" Incidence Rate based on recent 
experience (the number of new cases in the population during a specified period of time is called the "Incidence 
Rate"). 
“Family” means and includes Insured Person/Insured Person’s legal Spouse, Insured Person’s legal & dependent 
children and dependent parents 
“Grace Period” means the specified period of time  immediately following the premium due date during which a 
payment can be made to renew or continue a Policy in force without loss of continuity benefits such as waiting 
UIN: SBIHLIP21331V032021                  
Page 9 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
periods and coverage of Pre-existing  Diseases. Coverage is not available for the period for which no premium is 
received.  
“Hospital”: means any institution established for in- patient care and day care treatment of illness and / or injuries 
and which has been registered as a Hospital with the local authorities, under the Clinical Establishments (Registration 
and Regulation) Act, 2010 or under the enactments specified under the Schedule of Section 56(1) of the said Act OR 
complies with all minimum criteria as under: 
a. 
b. 
c. 
d. 
e. 
has qualified nursing staff under its employment round the clock; 
has at least 10 in-patient beds, in towns having population of less than 10,00,000 and at least 15 inpatient 
beds in all other places; 
has qualified Medical Practitioner (s) in charge round the clock; 
has a fully equipped operation theatre of its own where surgical procedures are carried out 
maintains daily records of patients and makes these accessible to the insurance company’s authorized 
personnel. 
“Hospitalisation” means admission in a Hospital for a minimum period of 24 In Patient Care consecutive ‘In-patient 
Care’ hours except for specified procedures/ treatments, where such admission could be for a period of less than 24 
consecutive hours.  
1. 
Illness 
Illness means a sickness or a disease or pathological condition leading to the impairment of normal 
physiological function which manifests itself during the Policy Period and requires medical treatment.  
a. 
Acute Condition- Acute condition is a disease, illness or injury that is likely to respond quickly to 
treatment which aims to return the person to his or her state of health immediately before suffering 
the disease/illness/injury which leads to full recovery. 
b.  
Chronic condition - A chronic condition is defined as a disease, illness, or injury that has one or more 
of the following characteristics:—  
1. it needs ongoing or long-term monitoring through consultations, examinations, check-ups, 
and / or tests— 
2. it needs ongoing or long-term control or relief of symptoms—  
3. it requires your rehabilitation or for you to be specially trained to cope with it— 
4. it continues indefinitely— 
5. it recurs or is likely to recur 
"Injury" means accidental physical bodily harm excluding illness or disease solely and directly caused by external, 
violent and visible means which is verified and certified by a Medical Practitioner. 
“Insured” means You/Your/Self/the person named in the Schedule, who is a citizen and resident of  India and for 
whom the insurance is proposed and appropriate premium paid. 
“Insured Person” means the person named in the Schedule/ who is a resident of India and for whom the insurance is 
proposed and appropriate premium paid. This includes Insured Person’s family.  
UIN: SBIHLIP21331V032021                  
Page 10 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
“Insurer” means Us/Our/We SBI General Insurance Company Limited. 
“Inpatient Care” means treatment for which the insured person has to stay in a hospital for more than 24 hours for a 
covered event.  
“Intensive Care Unit” means an identified section, ward or wing of a Hospital which is under the constant supervision 
of a dedicated Medical Practitioner(s), and which is specially equipped for the continuous monitoring and treatment 
of patients who are in a critical condition, or require life support facilities and where the level of care and supervision 
is considerably more sophisticated and intensive than in the ordinary and other wards. 
“Maternity expenses” shall include— 
a. 
medical treatment expenses traceable to childbirth ( including complicated deliveries and caesarean sections 
incurred during hospitalization). 
b. 
expenses towards lawful medical termination of pregnancy during the policy period. 
“Medical Advise” means any consultation or advice from a Medical Practitioner including the issue of any 
prescription or repeat prescription. 
“Medical Expenses” means those expenses that an Insured Person has necessarily and actually incurred for medical 
treatment on account of Illness or Accident on the advice of a Medical Practitioner, as long as these are no more 
than would have been payable if the Insured Person had not been insured and no more than other hospitals or 
doctors in the same locality would have charged for the same medical treatment.  
“Medically Necessary” Medically necessary treatment is defined as any treatment, tests, medication, or stay in 
hospital or part of a stay in hospital which 
a. is required for the medical management o f the illness or injury suffered by the insured; 
b. must not exceed the level o f care necessary to provide safe, adequate and appropriate medical care in 
scope, duration, or intensity; 
c. 
must have been prescribed by a medical practitioner, 
d. must conform to the professional standards widely accepted in international medical practice or by the 
medical community in India. 
“Medical Practitioner”: means a person who holds a valid registration from the medical  council of any State or 
Medical Council of India or Council for Indian Medicine or for Homeopathy set up by the Government of India or a 
State Governmentand is thereby entitled to practice medicine within its jurisdiction; and is acting within the scope 
and jurisdiction of license. The registered Medical Practitioner should not be the Insured or any one of the close 
family members of the Insured. 
“Mental Illness/Disease” means any mental Disease or bodily condition marked by disorganization of personality, 
mind, and emotions to impair the normal psychological, social or work performance of the individual regardless of its 
cause or origin. 
Migration” means, the right accorded to health insurance policyholders (including all members under family cover 
and members of group health insurance policy), to transfer the credit gained for pre-existing conditions and time 
bound exclusions, with the same insurer. 
UIN: SBIHLIP21331V032021                  
Page 11 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
“Network Provider” means hospitals or health care providers enlisted by an insurer or by a TPA and insurer together 
to provide medical services to an Insured  on payment by a cashless facility. 
“Newborn baby” means baby born during the Policy Period and is aged between 1 day and 90 days, both days 
inclusive. 
“Non- Network” means Any hospital, day care centre or other provider that is not part of the network. 
“Notification of claim”  
Notification of claim means the process of intimating a claim to the insurer or TPA through any of the recognized 
modes of communication. 
“Other Insurer” means any of the registered Insurers in India other than Us/Our/We SBI General Insurance Company 
Limited. 
“OPD treatment” is one in which the Insured visits a clinic / hospital or associated facility like a consultation room for 
diagnosis and treatment based on the advice of a Medical Practitioner. The Insured is not admitted as a day care or 
in-patient.  
Portability 
Portability” means, the right accorded to individual health insurance policyholders (including all members under 
family cover), to transfer the credit gained for pre-existing conditions and time bound exclusions, from one insurer to 
another insurer. 
“Package Service Expenses”: means expenses levied by the Hospitalfor treatment of specific surgical 
procedures/medical ailments as a lump sum amount under agreed package charges based on the room criteria as 
defined in the tariff Schedule of the Hospital. 
Pre-existing Disease means any condition, ailment, injury or disease: 
a) That is/are diagnosed by a physician within 48 months prior to the effective date of the policy issued 
by the insurer or its reinstatement or 
b) For which medical advice or treatment was recommended by, or received from, a physician within 48 
months prior to the effective date of the policy issued by the insurer or its reinstatement. 
“Policy Period” means the period commencing with the commencement date of the Policy & terminating with the 
expiry date of the Policy as stated in the Policy Schedule. 
“Pre-hospitalization Medical Expenses”  
Pre-hospitalization Medical Expenses means medical expenses incurred during predefined number of days preceding 
the hospitalization of the Insured Person, provided that: 
UIN: SBIHLIP21331V032021                  
Page 12 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
i. 
ii. 
Such Medical Expenses are incurred for the same condition for which the Insured Person’s 
Hospitalization was required, and 
The In-patient Hospitalization claim for such Hospitalization is admissible by the Insurance Company. 
“Post-hospitalization Medical Expenses”  
Post-hospitalization Medical Expenses means medical expenses incurred during predefined number of days 
immediately after the insured person is discharged from the hospital provided that: 
i. 
ii. 
Such Medical Expenses are for the same condition for which the insured person’s hospitalization was 
required, and 
The inpatient hospitalization claim for such hospitalization is admissible by the 
insurance company. 
“Proposal” means the written application or a standard form which the Insured duly fills and signs in with complete 
details seeking insurance are provided by him and includes any other information Insured provides to the insurer in 
the said form or in any communication with the Insurer seeking such insurance.  
“Proposer” means the person furnishing complete details and information in the Proposal form for availing the 
benefits either for himself or towards the person to be covered under the Policy and consents to the terms of the 
contract of Insurance by way of signing the same. 
“Qualified Nurse” means a person who holds a valid registration from the Nursing Council of India or the Nursing 
Council of any state in India. 
“Renewal” means the terms on which the contract of insurance can be renewed on mutual consent with a provision 
of grace period for treating the renewal continuous for the purpose of gaining credit for pre-existing diseases, time
bound exclusions and for all waiting periods. 
“Reasonable and Customary Charges” means the charges for services or supplies, which are the standard charges for 
the specific provider and consistent with the prevailing charges in the geographical area for identical or similar 
services, taking into account the nature of the illness / injury involved  
“Room Rent” means the amount charged by a Hospital towards Room and Boarding expenses and shall include the 
associated medical expenses. 
“Schedule” means that portion of the Policy which sets out Insured details, the type of Insurance cover in force, the 
Policy Period and the Sum Insured.  Any Annexure and/or Endorsement to the Schedule shall also be a part of the 
Schedule. 
“Sum Insured” means the specified amount mentioned in the Schedule to this Policy which represents the Insurer’s 
maximum liability for any or all claims under this policy during the currency of the Policy subject to terms and 
conditions as stated in the Policy. 
UIN: SBIHLIP21331V032021                  
Page 13 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
“Surgery/Surgical Procedure” means manual and/or operative procedures required for treatment of an Illness or 
Injury, correction of deformities and defects, diagnosis and cure of Diseases, relief of suffering or prolongation of life, 
performed in a Hospital or day care centre by a Medical Practitioner. 
“Unproven/Experimental treatment” means Treatment including drug experimental therapy which is not based on 
established medical practice in India, is treatment experimental or unproven. 
“Waiting Period:” No benefit shall be payable during the term of the Policy for the claim which occurs or where the 
hospitalisation for the claim has occurred within 30 days of first Policy issue Date. Waiting period is not applicable for 
the subsequent continuous uninterrupted renewals and hospitalisation due to accidents. 
Tele-consultation  
means engagement between licensed tele-consultation service provider/ professional and the insured/ covered 
member that is provided via a range of technology enabled communication media other than face-to-face 
interactions, such as telephone, internet, and others. 
SCOPE OF COVER 
Insurer shall pay the expenses reasonably and necessarily incurred by or on behalf of the Insured Person under the 
following categories but not exceeding the Sum Insured and subject to deduction of any deductible as reflected in the 
policy schedule in respect of such Insured person as specified in the Schedule: 
1. Room, Board & Nursing expenses as charged by the Hospital Excluding registration and service Expenses are 
covered up to 1% of the Sum Insured per day and  if admitted into Intensive Care Unit up to 2% of the Sum 
Insured per day under the policy.  
All admissible claims under Room, Board & Nursing Expenses including ICU, during the policy period are restricted 
maximum up to 25% of the Sum Insured per illness/injury. 
In case the insured opts for a higher room category than his eligibility the same can be covered upon specific 
acceptance by the insurer or Administrator.  In such a case  we shall not recover any expenses towards 
proportionate deductions other than the defined 'associate medical expenses' 
2. Medical Practitioner, Surgeon, Anesthetist, Consultants(Including Teleconsultation), and Specialists Fees - All 
admissible claims under this section during the policy period restricted maximum up to 40% of the Sum Insured 
per illness/injury. 
3. Anesthesia, Blood, Oxygen, Operation Theatre Expenses, Surgical Appliances, Medicines & consumables, 
Diagnostic expenses and X-ray, Dialysis, Chemotherapy, Radiotherapy, Cost of Pacemaker, prosthesis/internal 
implants and any medical Expenses incurred which is integral part of the operation - All admissible claims under 
this section during the policy period restricted maximum up to 40% of the Sum Insured per illness/injury. 
UIN: SBIHLIP21331V032021                  
Page 14 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
The amounts payable under points no. 2 and 3 shall be at the rate applicable to the entitled room category. In 
case the Insured opts for a room with rent higher than the entitled category as under point no. 1, the charges 
payable under point 1, 2 and 3 shall be limited to the charges applicable to the entitled category.  
4. Cataract Treatment: Our obligation to make payment in respect of any claim for treatment of Cataract including 
surgery thereof under the policy is limited to 15 % of the Sum Insured subject to a maximum of INR 25000 per 
eye and further subject to first two years exclusion for cataract as provided under the Policy. 
5. Pre-Hospitalisation Expenses: Pre-hospitalisation medical expenses incurred in 30 days subject to the condition 
that maximum amount that can be claimed under this head is limited to 10% of the Eligible Hospitalisation 
Expenses for each of the admitted hosipitalisation and domiciliary hospitalization claim under the Policy. 
6. Post-Hospitalisation Expenses: Post-hospitalisation medical expenses incurred in 60 days subject to the condition 
that maximum amount that can be claimed under this head is limited to 10% of the Eligible Hospitalisation 
Expenses for each of the admitted hosipitalisation  and domiciliary hospitalization claim under the Policy. 
7. Day Care Expenses: Insurer shall pay for Day Care Expenses incurred on technological surgeries and procedures 
requiring less than 24 hours of Hospitalisation as per Annexure A (day care procedure in the Policy), forming part 
of this Policy up to the Sum Insured. The day care Expenses will be payable only if, prior approval has been 
provided by the Administrator or Insurer for such a day care procedure.  
8. Ambulance Expenses: 1% of Sum Insured per Policy period up to a maximum of INR 1500 will be reimbursed to 
Insured for the cost of ambulance transportation. Ambulance services used should be of a licensed ambulance 
operator. 
9. Ayurvedic Medicine: Ayurvedic Treatment covered up to maximum 15% of Sum Insured per Policy Period up to a 
maximum of INR 20000 subject to treatment taken  in a government hospital or in any institute recognised by 
government and/or accredited by Quality Council of India/National Accreditation Board on Health.  
10.  Homeopathic and Unani system of medicine: Homeopathy and Unani Treatment covered up to maximum 10% 
of Sum Insured per Policy Period up to a maximum of INR 15000 subject to treatment taken  in a government 
hospital or in any institute recognised by government and/or accredited by Quality Council of India/National 
Accreditation Board on Health. 
11. Domiciliary Hospitalisation: Insurer will cover Reasonable and Customary Charges towards Domiciliary 
Hospitalisation exceeding 3 days ,subject to 20% of the Sum Insured maximum up to INR 20000 whichever is less 
and according to the definition of domiciliary Hospitalisation as given in the policy Schedule. however domiciliary 
Hospitalisation benefits shall not cover:- 
a. 
Asthma 
Expenses incurred for treatment for any of the following Diseases 
i. 
ii. 
iii. 
Bronchitis 
Chronic Nephritis and Nephritic Syndrome 
iv. Diarrhea and all type of Dysenteries including Gastro-enteritis 
v. Epilepsy 
vi. Influenza, Cough and Cold 
vii. Pyrexia of unknown Origin for less than 10 days 
viii. Tonsillitis and Upper Respiratory Tract Infection including Laryngitis and Pharingitis 
UIN: SBIHLIP21331V032021                  
Page 15 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
ix. Arthritis, Gout and Rheumatism 
12. Organ Donor: The Medical Expenses incurred for extraction of the required organ from the organ donor are 
covered under the policy  subject to  Insurer accepting the inpatient Hospitalisation claim made by the Insured 
and further provided that: 
a. 
b. 
c. 
The organ donor is the Insured Person’s blood relative or is an individual who can donate the organ as 
per the local law and as approved by the medical board of the hospital where the organ extraction is 
taking place and the organ donated is for the use of the Insured Person, and 
We will not pay the donor’s pre- and post-Hospitalisation expenses or any other medical treatment for 
the donor consequent on the organ extraction. 
All the expenses incurred on the donor/donee, as above would be within the overall Sum Insured of the 
Insured Person under the Policy and as specified in the policy Schedule. 
However, all admissible claims under above coverage’s during the policy period restricted maximum up to the 
Sum Insured as stated in the Policy Schedule per Policy Period. 
13. Free medical check-up: For every four claim-free consecutive years during which policyholder has been Insured 
with Insurer without any break in insurance, Insurer may arrange a free medical check-up for Insured in Insurer’s 
empanelled diagnostic centre or Insurer shall reimburse the cost incurred by Insured for the check-up subject to 
maximum 1% of Sum Insured up to a maximum of INR 2500. 
14. Parental Care: Available for persons above 60 years of age.   Insurer shall pay for the attendant nursing Expenses 
after discharge from the hospital for INR 500 or actual whichever is lesser per day up to a maximum 10 days per 
Hospitalisation of such Insured Person subject to the treating Medical Practitioner at the hospital where the 
Hospitalisation took place, recommending the duration of such nursing care requirement.  The Expenses can be 
reimbursed for a period not exceeding 15 days during the entire Policy period. The attendant nurse must qualify 
Insurer’s definition and attendance is required as per treating Medical Practitioner’s opinion. 
15. Accidental Hospitalisation -In case of hospitalization following an Accident, Sum Insured limit available for the 
Insured Person will be 125% of the amount arrived after deducting the claims paid and/or outstanding from sum 
insured as on the date of accident for the Insured Person under the policy and excluding cumulative bonus 
accrued.  Any such increase in sum insured over and above the base sum insured due to the operation of this 
clause would be restricted to a maximum of INR 1,00,000/- only.  This benefit is payable only once per Insured 
Person during the policy period and only once irrespective of number of such accidental hospitalisations during 
the policy period for policies covered under Family Floater cover. 
16. Child Care: Insurer shall pay for the attendant escort Expenses of INR 500 for each completed day of 
Hospitalisation of a child below 10 years of age, subject to maximum of 30 days during the Policy Period. Escort 
person includes mother, father, grandfather, grandmother and any immediate family member. 
17. Co-pay: For all admissible claims in non-network hospitals, Insured shall bear 10% of the admissible claim in 
addition to the deductible as per terms of insurance 
18. Convalescence Benefit: This benefit is available for Insured Person’s aged above 10 years & below 60 years and 
we shall pay an amount of INR 5,000/- per Insured, if the Insured Person is hospitalised for any bodily injury or 
illness as covered under the Policy, for a period of 10 consecutive days or more. This benefit is payable only once 
per Insured during the policy period. 
UIN: SBIHLIP21331V032021                  
Page 16 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
19. HIV/AIDS Cover: We will cover expenses incurred for Inpatient treatment  due to  any condition caused by 
or associated with human immunodeficiency virus or variant/mutant viruses and or any syndrome or 
condition of a similar kind commonly referred to as AIDS  upto the Limit Rs.50,000 except for the conditions 
which are permanently excluded 
20. Mental Illness Cover: We will cover for the expenses incurred for the inpatient Treatment for any mental illness 
or psychiatric or psychological ailment / condition upto the limit Rs.50,000 
21. Genetic Disorders or Diseases are covered up to the Limit Rs. 50,000 
22. Internal Congenital Diseases are Covered upto the Limit Rs. 10% of Sum Insured. 
23. The following procedures will be covered (wherever medically indicated) either as in patient or as part of day care 
treatment in a hospital up to 50% of -of Sum Insured, specified in the policy schedule, during the policy period:  
A. Uterine Artery Embolization and HIFU (High Intensity Focused Ultrasound)  
B. Balloon Sinuplasty  
C. Deep Brain Stimulation  
D. Oral Chemotherapy  
E. Immunotherapy - Monoclonal Antibody to be given as injection  
F. Intra Vitreal Injections  
G. Robotic Surgeries  
H. Stereotactic Radio Surgeries  
I. 
Bronchial Thermoplasty  
J. 
Vaporisation of the Prostrate ( Green Laser Treatment or Holmium Laser Treatment)  
K. IONM - (lntra Operative Neuro Monitoring) 
L. 
EXCLUSIONS 
Stem Cell Therapy: Hematopoietic stem cells for bone marrow transplant for haematological conditions 
to be covered 
We will not pay for any expenses incurred by Insured in respect of claims arising out of or howsoever related to any 
of the following: 
1. Pre-Existing Diseases - Code- Excl01 
a)    Expenses related to the treatment of a pre-existing Disease (PED) and its direct complications shall be 
excluded until the expiry of #### months of continuous coverage after the date of inception of the first policy 
with insurer. 
b)    In case of enhancement of sum insured the exclusion shall apply afresh to the extent of sum insured increase. 
c)    If the Insured Person is continuously covered without any break as defined under the portability norms of the 
extant IRDAI (Health Insurance) Regulations, then waiting period for the same would be reduced to the 
extent of prior coverage. 
d)    Coverage under the policy after the expiry of 48 months for any pre-existing disease is subject to the same 
being declared at the time of application and accepted by Insurer. 
UIN: SBIHLIP21331V032021                  
Page 17 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
2. 30-day waiting period- Code- Excl03  
a) Expenses related to the treatment of any illness within 30 days from the first policy commencement 
date shall be excluded except claims arising due to an accident, provided the same are covered. 
b) This exclusion shall not, however, apply if the Insured Person has Continuous Coverage for more 
than twelve months. 
c) The within referred waiting period is made applicable to the enhanced sum insured in the event of 
granting higher sum insured subsequently. 
3. Specified disease/procedure waiting period- Code- Excl02 
a)  Expenses related to the treatment of the listed Conditions, surgeries/treatments shall be excluded until the 
expiry of 90 Days/1 Year/2 Years/3 Years  of continuous coverage after the date of inception of the first policy 
with us. This exclusion shall not be applicable for claims arising due to an accident. 
b)   
c)   
d)   
e)   
f)   
In case of enhancement of sum insured the exclusion shall apply afresh to the extent of sum insured 
increase. 
If any of the specified disease/procedure falls under the waiting period specified for pre-Existing diseases, 
then the longer of the two waiting periods shall apply. 
The waiting period for listed conditions shall apply even if contracted after the policy or declared and 
accepted without a specific exclusion. 
If the Insured Person is continuously covered without any break as defined under the applicable norms on 
portability stipulated by IRDAI, then waiting period for the same would be reduced to the extent of prior 
coverage. 
List of specific diseases/procedures 
i. 
1 Year waiting period 
• Any types of gastric or duodenal ulcers,  
• Tonsillectomy, Adenoidectomy, Mastoidectomy, Tympanoplasty 
• Surgery on all internal or external tumor /cysts/nodules/polyps of any kind including breast lumps 
• All types of Hernia and Hydrocele 
• Anal Fissures, Fistula and Piles 
ii.2 Years Waiting Period 
• Cataract 
• Benign Prostatic Hypertrophy 
• Hysterectomy/ myomectomy for menorrhagia or fibromyoma or prolapse of uterus 
• Non infective Arthritis, Treatment of Spondylosis / Spondylitis, Gout & Rheumatism  
UIN: SBIHLIP21331V032021                  
Page 18 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
• Surgery of Genitourinary tract 
• Calculus Diseases of any etiology 
• Sinusitis and related disorders 
• Surgery for prolapsed intervertebral disc unless arising from accident 
• Surgery of varicose veins and varicose ulcers 
• Chronic Renal failure including dialysis 
iii. 
iv. 
3 Years Waiting Period 
• Medical Expenses incurred during or in connection with joint replacement surgery due to Degenerative 
condition, Age related osteoarthritis and Osteoporosis unless such joint replacement surgery is 
necessitated by accidental Bodily Injury. 
90 Days Waiting Period 
• Hypertension, Heart Disease and related complications  
• Diabetes and related complications 
4. Treatment outside India. 
5. War, invasion, acts of foreign enemies, hostilities (whether war be declared or not), civil war, commotion, 
unrest, rebellion, revolution, insurrection, military or usurped power or confiscation or nationalisation or 
requisition of or damage by or under the order of any government or public local authority. 
6. Injury or Disease directly or indirectly caused by or contributed to by nuclear weapons/materials. 
7. Circumcision unless necessary for treatment of a disease, illness or injury not excluded hereunder, or, as may 
be necessitated due to an accident  
8. Refractive Error: (Code- Excl15) 
Expenses related to the treatment for correction of eye sight due to refractive error less than 7.5 dioptres. 
9. Cosmetic or plastic Surgery: (Code- Excl08) 
Expenses for cosmetic or plastic surgery or any treatment to change appearance unless for reconstruction 
following an Accident, Burn(s) or Cancer or as part of medically necessary treatment to remove a direct and 
immediate health risk to the insured. For this to be considered a medical necessity, it must be certified by the 
attending Medical Practitioner. 
10. The cost of spectacles, contact lenses, hearing aids, crutches, wheelchairs, artificial limbs, dentures, artificial 
teeth and all other external appliances. Prosthesis and/or devices. 
11. Expenses incurred on Items for personal comfort like television, telephone, etc. incurred during 
hospitalization and which have been specifically charged for in the hospitalisation bills issued by the hospital.   
12. External medical equipment of any kind used at home as post Hospitalisation care including cost of 
instrument used in the treatment of Sleep Apnoea Syndrome (C.P.A.P), Continuous Ambulatory Peritoneal 
Dialysis (C.A.P.D) and Oxygen concentrator for Bronchial Asthmatic condition. 
13. Dental treatment or surgery of any kind unless required as a result of Accidental Bodily Injury to natural teeth 
requiring hospitalization treatment. 
14. Convalescence, general debility, “Run-down” condition, rest cure, Congenital  external illness/disease/defect. 
15. Intentional self-injury (including but not limited to the use or misuse of any intoxicating drugs or 
alcohol) 
16. Breach of law: (Code- Excl10 ) 
Expenses for treatment directly arising from or consequent upon any Insured Person committing or 
UIN: SBIHLIP21331V032021                  
Page 19 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
attempting to commit a breach of law with criminal intent. 
17. Treatment for, Alcoholism, drug or substance abuse or any addictive condition and consequences thereof. 
(Code- Excl12) 
18. Venereal disease or any sexually transmitted disease or sickness. (excluding HIV / AIDS as mentioned under 
scope of cover ) 
19. Maternity Expenses (Code - Excl 18): 
i. 
ii. 
Medical treatment expenses traceable to childbirth (including complicated deliveries and caesarean 
sections incurred during hospitalization) except ectopic pregnancy; 
expenses towards miscarriage (unless due to an accident) and lawful medical termination of 
pregnancy during the policy period. 
20. Sterility and Infertility: (Code- Excl17) 
Expenses related to sterility and infertility this includes: 
i. 
Any type of sterilization 
ii. 
iii. 
Assisted Reproduction services including artificial insemination and advanced reproductive   
technologies such as IVF, ZIFT, GIFT ICSI 
Gestational Surrogacy 
iv. Reversal of sterilization  
21. Dietary supplements and substances that can be purchased without prescription, including but not limited to 
Vitamins, minerals and organic substances unless prescribed by a medical practitioner as part of 
hospitalization claim or day care procedure. (Code- Excl14) 
22. Vaccination or inoculation except as part of post-bite treatment for animal bite. 
23. Surgery to correct deviated septum and hypertrophied turbinate unless necessitated by an accidental body 
injury and proved to our satisfaction that the condition is a result of an accidental injury. 
24. Medical Practitioner’s home visit Expenses during pre and post hospitalization period, Attendant Nursing 
Expenses unless more than 60 years as specified in the parental care benefit. 
25. Change-of-Gender treatments: (Code- Excl07) 
Expenses related to any treatment, including surgical management, to change characteristics of the  body to 
those of the opposite sex. 
26. Outpatient Diagnostic, Medical and Surgical procedures or treatments, non-prescribed drugs and   medical 
supplies, 
27. Hazardous or Adventure sports: (Code- Excl09) 
Expenses related to any treatment necessitated due to participation as a professional in hazardous  or  
adventure sports, including but not limited to, para-jumping, rock climbing, mountaineering, rafting, motor  
racing, horse racing or scuba diving, hand gliding, sky diving, deep-sea diving. 
28. Treatments received in heath hydros, nature cure clinics, spas or similar establishments or private beds 
registered as a nursing home attached to such establishments or where admission is arranged wholly or 
partly for domestic reasons. (Code- Excl13) 
29. Rest Cure, rehabilitation and respite care- (Code- Excl05) 
a)     
Expenses related to any admission primarily for enforced bed rest and not for receiving treatment. This 
also includes: 
UIN: SBIHLIP21331V032021                  
Page 20 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
i. 
ii. 
Custodial care either at home or in a nursing facility for personal care such as help with activities of 
daily living such as bathing, dressing, moving around either by skilled nurses or assistant or non-skilled 
persons. 
Any services for people who are terminally ill to address physical, social, emotional and spiritual needs. 
30. Treatment with alternative medicines like acupuncture, acupressure, osteopath, naturopathy, chiropractic, 
reflexology and aromatherapy. 
31. Investigation & Evaluation- Code- Excl04 
a) Expenses related to any admission primarily for diagnostics and evaluation purposes only are excluded. 
b) Any diagnostic expenses which are not related or not incidental to the current diagnosis and treatment are 
excluded. 
32. Hospitalization for donation of any body organs by an Insured Person including complications arising from 
the donation of organs. 
33. Obesity/ Weight Control: (Code- Excl06) 
Expenses related to the surgical treatment of obesity that does not fulfil all the below conditions: 
1) Surgery to be conducted is upon the advice of the Doctor 
2) The surgery/Procedure conducted should be supported by clinical protocols 
3) The member has to be 18 years of age or older and 
4) Body Mass Index (BMI); 
a) greater than or equal to 40 or 
b) greater than or equal to 35 in conjunction with any of the following severe co-morbidities 
Following failure of less invasive methods of weight loss: 
i. 
ii. 
iii. 
Obesity-related cardiomyopathy 
Coronary heart disease 
Severe Sleep Apnea 
iv. Uncontrolled Type2 Diabetes 
34.  Unproven Treatments: (Code- Excl16) 
Expenses related to any unproven treatment, services and supplies for or in connection with any treatment. 
Unproven treatments are treatments, procedures or supplies that lack significant medical documentation to 
support their effectiveness. 
35. Costs of donor screening or treatment 
36. Disease / injury illness whilst performing duties as a serving member of a military or police force. 
37.  Any kind of Service charges, Surcharges, Admission fees / Registration charges etc levied by the hospital. 
38. In respect of the existing diseases, disclosed by the insured and mentioned in the policy schedule (based 
on insured's consent), policyholder is not entitled to get the coverage for specified ICD codes. 
GENERAL CONDITIONS 
1. Condition Precedent to Admission of Liability 
The terms and conditions of the policy must be fulfilled by the insured person for the Company to make any  
payment for claim(s) arising under the policy. 
2. 
Free look period 
UIN: SBIHLIP21331V032021                  
Page 21 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
The Free Look Period shall be applicable on new individual health insurance policies and not on renewals or at the 
time of porting/migrating the policy. 
The insured person shall be allowed free look period of fifteen days from date of receipt of the policy document to 
review the terms and conditions of the policy, and to return the same if not acceptable. 
If the insured has not made any claim during the Free Look Period, the insured shall be entitled to 
iii.   
a refund of the premium paid less any expenses incurred by the Company on medical examination of 
the insured person and the stamp duty charges or 
iv. where the risk has already commenced and the option of return of the policy is exercised by the 
insured person, a deduction towards the proportionate risk premium for period of cover or 
v.  
3. 
Where only a part of the insurance coverage has commenced, such proportionate premium 
commensurate with the insurance coverage during such period; 
Disclosure to Information Norm: 
The policy shall be void and all premium paid thereon shall be forfeited to the Company in the event of 
misrepresentation, mis description or non-disclosure ofany material fact by the policyholder. 
(Explanation: "Material facts" for the purpose of this policy shall mean all relevant information sought by the 
company in the proposal form and other connected documents to enable it to take informed decision in the 
context of underwriting the risk) 
4. 
5. 
6. 
Complete Discharge 
Any payment to the policyholder, insured person or his/ her nominees or his/ her legal representative or assignee 
or to the Hospital, as the case may be, for any benefit under the policy shall be a valid discharge towards payment 
of claim by the Company to the extent of that amount for the particular claim. 
Due Care 
Where this Policy requires Insured to do or not to do something, then the complete satisfaction of that 
requirement by Insured or someone claiming on Insured behalf is a precondition to any obligation under this 
Policy. If Insured or someone claiming on Insured behalf fails to completely satisfy that requirement, then Insurer 
may refuse to consider Insured claim. Insured will cooperate with Insurer at all times. 
Mis-description 
This Policy shall be void and premium paid shall be forfeited to Insurer in the event of misrepresentation, mis
description or non-disclosure of any materials facts pertaining to the proposal form, written declarations or any 
other communication exchanged for the sake of obtaining the Insurance policy by the Insured.   Nondisclosure 
shall include non-intimation of any circumstances which may affect the insurance cover granted.  The 
Misrepresentation, mis-description and non-disclosure is related to the information provided by the 
proposer/insured to the Insurer at any point of time starting from seeking the insurance cover in the form of 
submitting the filled in proposal form, written declarations or any other communication exchanged for the sake 
of obtaining the Insurance policy and ends only after all the Contractual obligations under the policy are 
exhausted for both the parties under the contract. 
UIN: SBIHLIP21331V032021                  
Page 22 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
7. 
8. 
9. 
10. 
11. 
Insured Person 
Only those persons named as the Insured Person in the Schedule shall be covered under this Policy. The details of 
the Insured Person are as provided by Insured. A person may be added as an Insured Person during the Policy 
Period after Insured’s Proposal has been accepted by Insurer, an additional premium has been paid and Insurer’s 
agreement to extend cover has been indicated by it issuing an endorsement confirming the addition of such 
person as an Insured. Cover under this Policy shall be withdrawn from any Insured Person upon such Insured 
giving 15 days written notice to be received by Insurer 
Package Service Expenses as defined under the policy will be payable only if prior approval for the said package 
service is provided by Administrator / Insurer upon the request of the Insured Person or Insured. 
Communications 
a. Any communication meant for Insurer must be in writing and be delivered to Insurer’s address shown in the 
Schedule. Any communication meant for Insured will be sent by Insurer to Insured’s address shown in the 
Schedule/Endorsement. 
b. All notifications and declarations for Insurer must be in writing and sent to the address specified in the 
Schedule. Agents are not authorized to receive notices and declarations on Insurer’s behalf. 
c. 
Insured must notify Insurer of any change in address. 
Unhindered access 
The Insured/Insured person shall extend all possible support & co-operation including necessary authorisation 
to the insurer for accessing the medical records and medical practitioners who have attended to the patient. 
Claims Procedures   
a. Claims Procedure for Reimbursement 
i. 
ii. 
iii. 
The Insured shall without any delay consult a Doctor and follow the advice and treatment 
recommended, take reasonable step to minimize the quantum of any claim that might be made under 
this Policy and intimation to this effect must be forwarded to Insurer accordingly. 
Insured must provide intimation to Insurer immediately and in any event within 48 hours from the date 
of Hospitalisation . However the Insurer at his sole discretion may relax this condition subject to a 
justifiable reason/evidence being produced by the Insured on the reasons for such a delay beyond the 
stipulated 48 hours up to a maximum period of 7 days.   
Insured has to file the claim with all necessary documentation within 15 days of discharge from the 
Hospital, provide Insurer with written details of the quantum of any claim along with all the original bills, 
receipts and other documents upon which a claim is based and shall also give Insurer such additional 
information and assistance as Insurer may require in dealing with the claim. In case of delayed 
submission of claim and in absence of a justified reason for delayed submission of claim, the Insurer 
would have the right of not considering the claim for reimbursement. 
iv. In respect of post hospitalization claims, the claims must be lodged within 15days from the completion of 
post Hospitalisation treatment subject to maximum of 75 days from the date of discharge from hospital. 
v. The Insured shall submit himself for examination by the Insurer’s medical advisors as often as may be 
considered necessary by the Insurer for establishing the liability under the Policy.  The Insurer will 
reimburse the amount towards the expenses incurred for the said medical examination to the Insured. 
vi. Insured must submit all original bills, receipts, certificates, information and evidences from the attending 
Medical Practitioner /Hospital /Diagnostic Laboratory as required by Insurer. 
UIN: SBIHLIP21331V032021                  
Page 23 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
vii. On receipt of intimation from Insured regarding a claim under the policy, Insurer/Administrator is 
entitled to carry out examination and obtain information on any alleged Injury or Disease requiring 
Hospitalisation if and when Insurer may reasonably require. 
b. Claims procedure for Cashless 
Administrator will provide the User guide & identity card to Insured. User guide will have following details: 
a. 
Contact details of all Administrator offices 
b. 
c. 
d. 
Website address of Administrator 
Network list of hospitals with their contact details 
Claim submission guidelines. 
c. Claims Submission 
Insured will submit the claim documents to administrator. Following is the document list for claim 
submission: 
i. 
ii. 
iii. 
Duly filled Claim form,  
Valid Photo Identity Card 
Original Discharge card/certificate/ death summary 
iv. Copies of prescription for diagnostic test, treatment advise, medical references 
v. Original set of investigation reports 
vi. Itemized original hospital bill and receipts Hospital and related original medical expense receipt 
Pharmacy bills in original with prescriptions 
d. Claims Processing 
On receipt of claim documents from Insured, Insurer/Administrator shall assess the admissibility of claim as 
per Policy terms and conditions.   Upon satisfactory completion of assessment and admission of claim, the 
Insurer will make the payment of benefit as per the contract.  In case the claim is repudiated Insurer will 
inform the Insured about the same in writing with reason for repudiation.  
12. 
13. 
Penal Interest Provision  
1. The Company shall settle or reject a claim, as the case may be, within 30 days from the date of receipt 
of last necessary document. 
2. ln the case of delay in the payment of a claim, the Company shall be liable to pay interest to the 
policyholder from the date of receipt of last necessary document to the date of payment of claim at a 
rate 2% above the bank rate. 
3. However, where the circumstances of a claim warrant an investigation in the opinion of the Company, it 
shall initiate and complete such investigation at the earliest, in any case not later than 30 days from the 
date of receipt of last necessary document- ln such cases, the Company shall settle or reject the claim 
within 45 days from the date of receipt of last necessary document. 
4. ln case of delay beyond stipulated 45 days, the Company shall be liable to pay interest to the 
policyholder at a rate 2% above the bank rate from the date of oreceipt of last necessary document to 
the date of payment of claim. 
Cumulative Bonus  
If no claim has been made under the policy with us and the policy is renewed with us and without any break or 
within the Grace period as defined under the policy, we will allow a cumulative bonus to the renewal policy upon 
receipt of premium automatically by increasing the Sum Insured by 5%. The maximum cumulative bonus shall not 
exceed 25% of the Sum Insured in any policy year. The cumulative bonus to be offered is as mentioned below: 
UIN: SBIHLIP21331V032021                  
Page 24 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
a. 
b. 
c. 
d. 
e. 
14. 
In case of a family floater cover, the cumulative bonus so applied will depend on the claim/claims made 
under the expiring policy and will be 5% of Sum Insured for a claim free year and subject to a maximum 
of 25% of Sum Insured in any policy year. 
In case of a claim in the Policy the Cumulative Bonus if any under the policy will get reduced by 5% at the 
time of renewal, in the renewed policy.  Also, in case of a policy issued to a Family with specific Sum 
Insured to Insured Persons, the Cumulative Bonus, if any for the Insured Person who has made the claim 
under the policy gets reduced by 5% in the following year in the renewed policy. 
In case of a policy being renewed with us and which was previously covered with other Indian Insurers, 
we will be offering a maximum cumulative bonus of 20% of Sum Insured provided the Insured submits 
the renewal notice and policy copy reflecting a no claim bonus/cumulative bonus equivalent or more 
than 25%.  In case of no claim bonus enjoyed with previous Insurers being less than 25%, a deduction of 
5% will be made from the % of no claim bonus enjoyed and the balance will be allowed under the policy, 
as no claim bonus/cumulative bonus.  However, this benefit will be restricted only up to the sum insured 
as provided under the previous or expiring policy obtained by the Insured from Other Insurer. 
In case of increase in the Sum Insured on renewal of the Policy Cumulative bonus will be applicable on 
the increased Sum Insured only from the next year subject to no claims and will start from 5% and may / 
may not be similar to the cumulative bonus on the basic Sum Insured at the inception of the Policy with 
us.  
The accumulated cumulative bonus is available to the insured person only upon exhaustion of the basic 
sum insured under the policy and all the eligibility criteria for the ascertaining the applicable limits under 
the policy will be calculated basing on the base sum insured. 
Basis of claims payment 
a. If Insured suffer a relapse within 45 days of the discharge from Hospital, obtaining medical treatment or 
consulting a Doctor and for which a claim has been made, then such relapse shall be deemed to be part of 
the same claim, as long as the relapse occurs within the Policy Period. 
b. The day care procedures listed are subject to the exclusions, terms and conditions of the Policy and will not 
be treated as independent coverage under the Policy. 
c. 
The plan which Insured is covered for will be shown on the Schedule. The table below sets out the 
percentage of the eligible claim amount that Insurer will be accountable for where a claim cost is incurred in 
a Location other than that prescribed in the Schedule. 
Benefit Plan 
Treatment 
Location A
Mumbai and Delhi 
Plan A (Normal residential location -Mumbai 
& Delhi)  
100% 
Treatment 
Location B 
Chennai, Kolkata, 
Bangalore, 
Ahmedabad, 
Hyderabad 
100% 
Treatment 
Location C- Rest of 
India 
100% 
Plan B (Normal residential location -Chennai, 
Kolkata, Bangalore, Ahmedabad, Hyderabad 
) 
80% 
100% 
100% 
Plan C (Normal residential location -Rest of 
India ) 
70% 
80% 
100% 
• Plan A - 100% of the admissible claim amount for all Locations subject to the Policy terms and conditions. 
UIN: SBIHLIP21331V032021                  
Page 25 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
• Plan B - 100% of the admissible claim amount for Locations B and C, and 80% for Location A subject to 
the Policy terms and conditions.,  
• Plan C - 100% of the admissible claim amount for Locations C, 80% for Location B and 70% for Location A 
subject to the Policy terms and conditions.  
The percentage of amount shown in the above table is with respect to the admissible claim amount.  The Insurer 
will make payments only after being satisfied, with the necessary bills and documents submitted with reference 
to the claim. 
15. 
16. 
Multiple policies 
i.  
ii.  
iii.    
iv.   
In case of multiple policies taken by an insured person during a period from one or more insurers to 
indemnify treatment costs, the insured person shall have the right to require a settlement of his/her claim in 
terms of any of his/her policies. In all such cases the insurer chosen by the insured person shall be obliged to 
settle the claim as long as the claim is within the limits of and according to the terms of the chosen policy. 
Insured person having multiple policies shall also have the right to prefer claims under this policy for the 
amounts disallowed under any other policy / policies even if the sum insured is not exhausted. Then the 
insurer shall independently settle the claim subject to the terms and conditions of this policy. 
If the amount to be claimed exceeds the sum insured under a single policy, the insured person shall have the 
right to choose insurer from whom he/she wants to claim the balance amount. 
Where an insured person has policies from more than one insurer to cover the same risk on indemnity basis, 
the insured person shall only be indemnified the treatment costs in accordance with the terms and conditions 
of the chosen policy. 
Fraud:  
lf any claim made by the insured person, is in any respect fraudulent, or if any false statement, or declaration 
is made or used in support thereof, or if any fraudulent means or devices are used by the insured person or 
anyone acting on his/her behalf to obtain any benefit under this policy, all benefits under this policy and the 
premium paid shall be forfeited. 
Any amount already paid against claims made under this policy but which are found fraudulent later shall be 
repaid by all recipient(s)/policyholder(s), who has made that particular claim, who shall be jointly and 
severally liable for such repayment to the insurer. 
For the purpose of this clause, the expression "fraud" means any of the following acts committed by the 
insured person or by his agent or the hospital/doctor/any other pa(y acting on behalf of the insured person, 
with intent to deceive the insurer or to induce the insurer to issue an insurance policy: 
a) the suggestion, as a fact of that which is not true and which the insured 
person does not believe to be true; 
b) the active concealment of a fact by the insured person having knowledge 
or belief of the fact; 
c) any other act fitted to deceive; and 
d) any such act or omission as the law specially declares to be fraudulent 
The Company shall not repudiate the claim and / or forfeit the policy benefits on the ground of Fraud, if the 
insured person / beneficiary can prove that the misstatement was true to the best of his knowledge and 
UIN: SBIHLIP21331V032021                  
Page 26 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
there was no deliberate intention to suppress the fact or that such misstatement of or suppression of 
material fact are within the knowledge of the insurer. 
17.  
18. 
19. 
20. 
Cancellation  
1. The policyholder may cancel this policy by giving 1Sdays'written notice and in such an event, the 
Company shall refund premium for the unexpired policy period as detailed below. 
Period on risk 
Rate of premium refunded 
Up to one month 
75% of annual rate 
Up to three months 
50%of annual rate 
Up to six months 
25% of annual rate 
Exceeding six months Nil 
Notwithstanding anything contained herein or otheruise, no refunds of premium shall be made in respect of 
Cancellation where, any claim has been admitted or has been lodged or any benefit has been availed by the 
insured person under the policy. 
2. The Company may cancel the policy at any time on grounds of misrepresentation non-disclosure of 
material facts, fraud by the insured person by giving 15 days' written notice. There would be no refund 
of premium on cancellation on grounds or misrepresentation, non-disclosure of material facts or fraud. 
Termination of Policy 
This Policy terminates on earliest of the following events- 
a. 
Cancellation of policy as per the cancellation provision. 
b. 
On the policy expiry date. 
Renewal:  
The policy shall ordinarily be renewable except on misrepresentation by the insured person. grounds of 
fraud, 
vi. 
The Company shall endeavor to give notice for renewal. However, the Company is not under 
obligation to give any notice for renewal. 
vii. 
viii. 
ix.  
x.  
Renewal shall not be denied on the ground that the insured person had made a claim or claims in 
the preceding policy years. 
Request for renewal along with requisite premium shall be received by the Company before the 
end of the policy period. 
At the end of the policy period, the policy shall terminate and can be renewed within the Grace 
Period of 30 days  to maintain continuity of benefits without break in policy. Coverage is not 
available during the grace period. 
No loading shall apply on renewals based on individual claims experience 
Withdrawal of Product  
UIN: SBIHLIP21331V032021                  
Page 27 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
i. ln the likelihood of this product being withdrawn in future, the Company will intimate the insured person about the 
same 90 days prior to expiry of the policy.  
ii. Insured Person will have the option to migrate to similar health insurance product available with the Company at 
the time of renewal with all the accrued continuity benefits such as cumulative bonus, waiver of waiting period. as 
per IRDAI guidelines, provided the policy has been maintained without a break. 
. 
21. 
22. 
Migration 
The insured person will have the option to migrate the policy to other health insurance products/plans 
offered by the company by applying for migration of the policyatleast30 days before the policy renewal date 
as per IRDAI guidelines on Migration. If such person is presently covered and has been continuously covered 
without any lapses under any health insurance product/plan offered by the company, the insured person will 
get the accrued continuity benefits in waiting periods as per IRDAI guidelines on migration. 
For Detailed Guidelines on migration, kindly refer the link 
https://www.irdai.gov.in/ADMINCMS/cms/whatsNew_Layout.aspx?page=PageNo3987&flag=1 
Nomination  
The policyholder is required at the inception of the policy to make a nomination for the purpose of payment of 
claims under the policy in the event of death of the policyholder. Any change of nomination shall be 
communicated to the company in writing and such change shall be effective only when an endorsement on the 
policy is made. ln the event of death of the policyholder, the Company will pay the nominee {as named in the 
Policy Schedule/Policy Certificate/Endorsement (if any)} and in case there is no subsisting nominee, to the legal 
heirs or legal representatives of the policyholder whose discharge shall be treated as full and final discharge of its 
liability under the policy. 
23. 
Portability 
The insured person will have the option to port the policy to other insurers by applying to such insurer to port the 
entire policy along with all the members of the family, if any, at least 45 days before, but not earlier than 60 days 
from the policy renewal date as per IRDAI guidelines related to portability. lf such person is presently covered and has 
been continuously covered without any lapses under any health insurance policy with an lndian General/Health 
insurer, the proposed insured person will get the accrued continuity benefits in waiting periods as per IRDAI 
guidelines on portability. 
For Detailed Guidelines on portability, kindly refer the link . 
https://www.irdai.gov.in/ADMINCMS/cms/whatsNew_Layout.aspx?page=PageNo3987&flag=1 
24. 
Moratorium Period 
After completion of eight continuous years under the policy no look back to be applied. This period of eight years is 
called as moratorium period. The moratorium would be applicable for the sums insured of the first policy and 
subsequently completion of 8 continuous years would be applicable from date of enhancement of sums insured only 
on the enhanced limits. After the expiry of Moratorium Period no health insurance claim shall be contestable except 
for proven fraud and permanent exclusions specified in the policy contract. The policies would however be subject to 
all limits, sub limits, co-payments, deductibles as per the policy contract. 
UIN: SBIHLIP21331V032021                  
Page 28 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
25. 
26. 
27. 
28. 
29. 
30. 
31. 
32. 
Possibility of Revision of Terms of the Policy including the Premium Rates 
The Company, with prior approval of lRDAl, may revise or modify the terms of the policy including the premium 
rates. The insured person shall be notified three months before the changes are effected. 
Dispute Resolution 
a. If any dispute or difference shall arise as to the quantum to be paid under this Policy ( liability being 
otherwise admitted) such difference shall independently of all other questions be referred to the decision of 
a sole Arbitrator to be appointed in writing by the parties to the dispute/difference, or if they cannot agree 
upon a single Arbitrator within 30 days of any party invoking arbitration, the same shall be referred to a panel 
of 3 Arbitrators, one arbitrator to be appointed by each of the parties to the dispute/difference and the third 
Arbitrator to be appointed by such two Arbitrators and the arbitration shall be conducted under and in 
accordance with the provisions of the Arbitration and Conciliations Act 1996. 
b. It is hereby agreed and understood that no dispute or difference shall be referable to arbitration, as 
hereinbefore provided, if the Insurer has disputed or not accepted liability under or in respect of this Policy. 
c. It is expressly stipulated and declared that it shall be a condition precedent to any right of action or suit upon 
this Policy that the award by such Arbitrator/Arbitrators of the amount of the loss shall be first obtained. 
The law of the arbitration shall be Indian law and the seat of the arbitration and venue for all the hearings 
shall be within India. 
Examination of Medical Records:  
Insurer may examine Insured Person’s medical records/reports and related documents relating to the insurance 
under this Policy at any time during the Policy Period and up to three years after the Policy expiry, or until final 
adjustment (if any) and resolution of all claims under this Policy 
Geographical limits:  
All medical/surgical treatments under this policy shall have to be taken in India and admissible claims thereof 
shall be payable in Indian currency.  All matters or disputes arising hereunder the policy shall be determined in 
accordance with the law and practice of such Court within the Indian Territory. 
Observance of terms and conditions:  
The due observance and fulfillment of the terms,  conditions and endorsements of this Policy in so far as they 
relate to anything to be done or complied with by the Insured / Insured Person, shall be a condition precedent to 
any liability of the Insurer  to make any payment under this Policy. 
Forfeiture of claims:  
If any claim is made and rejected and no court action or suit commenced within 12 months after such rejection 
or, in case of arbitration taking place as provided herein, within 12 calendar months after the Arbitrator or 
Arbitrators have made their award, all benefits under this Policy shall be forfeited. 
Position after a claim:  
As from the day of receipt of the claim amount by the Insured/Insured Person, the Sum Insured and / or duration 
of cover for the remainder of the period of insurance shall stand reduced by a corresponding amount. 
Payment of Claims in case of death during hospitalisation:  
UIN: SBIHLIP21331V032021                  
Page 29 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
In the event of death of Primary Insured person on whose behalf covered medical expenses are incurred, such 
admissible claim amount would be payable to the legal heirs of the Primary Insured Person and If the diseased 
person is other than the primary insured person under the policy, we will pay such admissible claim amounts to 
the Primary Insured Person.  The primary insured person is the head of the family and who is the primary earning 
member for the family. 
33. 
34. 
Section 80 D Income-Tax Act:  
The premium paid is exempted from Income Tax under Sec 80 D of Income Tax act. 
Redressal of Grievance 
In case of any grievance the insured person may contact the company through 
Website: www.sbigeneral.in  
Toll free: 1800 22 1111 / 1800 102 1111 Monday to Saturday (8 am - 8 pm). 
E-mail: customer.care@sbigeneral.in 
Fax : 1800 22 7244 / 1800 102 7244 
Courier:  
Insured person may also approach the grievance cell at any of the company’s branches with the details of 
grievance 
If Insured person is not satisfied with the redressal of grievance through one of the above methods, insured 
person may contact the grievance officer at gro@sbigeneral.in  
For updated details of grievance officer, kindly refer the link https://www.sbigeneral.in/portal/grievance
redressal 
If Insured person is not satisfied with the redressalof grievance through above methods, theinsured person may 
also approach the office of Insurance Ombudsman of the respective area/region for redressal of grievanceas per 
Insurance Ombudsman Rules 2017.  
Office of Insurance the Ombudsman 
Areas of Jurisdiction  
Gujarat, Dadra & Nagar Haveli,Daman and Diu. 
AHMEDABAD - Shri Kuldip Singh 
Office of the Insurance Ombudsman, 
Jeevan Prakash Building, 6th floor, 
Tilak Marg, Relief Road, 
Ahmedabad – 380 001. 
Tel.: 079 - 25501201/02/05/06 
Email: bimalokpal.ahmedabad@ecoi.co.in 
UIN: SBIHLIP21331V032021                  
Page 30 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
 
SBI General Insurance Company Limited                                   
                                                       
 
 
SBI General Insurance Company Limited Health Insurance Policy- Retail                     UIN: SBIHLIP21331V032021                  Page 31 of 45  
BENGALURU - Smt. Neerja Shah 
Office of the Insurance Ombudsman, 
Jeevan Soudha Building,PID No. 57-27-N-19 
Ground Floor, 19/19, 24th Main Road, 
JP Nagar, Ist Phase, 
Bengaluru – 560 078. 
Tel.: 080 - 26652048 / 26652049 
Email: bimalokpal.bengaluru@ecoi.co.in 
Karnataka. 
BHOPAL - Shri Guru Saran Shrivastava  
Office of the Insurance Ombudsman, 
JanakVihar Complex, 2nd Floor,  
6, Malviya Nagar, Opp. Airtel Office, 
Near New Market, 
Bhopal – 462 003. 
Tel.: 0755 - 2769201 / 2769202 
Fax: 0755 - 2769203 
Email: bimalokpal.bhopal@ecoi.co.in 
               Madhya Pradesh, Chhattisgarh. 
BHUBANESHWAR - Shri Suresh Chnadra Panda  
Office of the Insurance Ombudsman, 
62, Forest park, 
Bhubneshwar – 751 009. 
Tel.: 0674 - 2596461 /2596455 
Fax: 0674 - 2596429 
Email: bimalokpal.bhubaneswar@ecoi.co.in 
Orissa. 
CHANDIGARH - Dr. Dinesh Kumar Verma  
Office of the Insurance Ombudsman, 
S.C.O. No. 101, 102 & 103, 2nd Floor, 
Batra Building, Sector 17 – D, 
Chandigarh – 160 017. 
Tel.: 0172 - 2706196 / 2706468 
Fax: 0172 - 2708274 
Email: bimalokpal.chandigarh@ecoi.co.in 
Punjab,Haryana, 
Himachal Pradesh, 
Jammu & Kashmir, 
Chandigarh. 
CHENNAI - Shri M. Vasantha Krishna  
Office of the Insurance Ombudsman, 
Fatima Akhtar Court, 4th Floor, 453,  
Anna Salai, Teynampet, 
CHENNAI – 600 018. 
Tel.: 044 - 24333668 / 24335284 
Fax: 044 - 24333664 
Email: bimalokpal.chennai@ecoi.co.in 
Tamil Nadu, 
Pondicherry Town and 
Karaikal (which are part of UT of Pondicherry). 
 
SBI General Insurance Company Limited                                   
                                                       
 
 
SBI General Insurance Company Limited Health Insurance Policy- Retail                     UIN: SBIHLIP21331V032021                  Page 32 of 45  
DELHI - Shri Sudhir Krishna   
Office of the Insurance Ombudsman, 
2/2 A, Universal Insurance Building, 
Asaf Ali Road, 
New Delhi – 110 002. 
Tel.: 011 - 23232481/23213504 
Email: bimalokpal.delhi@ecoi.co.in 
Delhi. 
GUWAHATI - Shri Kiriti .B. Saha 
Office of the Insurance Ombudsman, 
Jeevan Nivesh, 5th Floor, 
Nr. Panbazar over bridge, S.S. Road, 
Guwahati – 781001(ASSAM). 
Tel.: 0361 - 2632204 / 2602205 
Email: bimalokpal.guwahati@ecoi.co.in 
Assam, Meghalaya, 
Manipur, Mizoram, 
Arunachal Pradesh, 
Nagaland and Tripura. 
HYDERABAD - Shri I. Suresh Babu 
Office of the Insurance Ombudsman, 
6-2-46, 1st floor, "Moin Court", 
Lane Opp. Saleem Function Palace,  
A. C. Guards, Lakdi-Ka-Pool, 
Hyderabad - 500 004. 
Tel.: 040 - 67504123 / 23312122  
Fax: 040 - 23376599 
Email: bimalokpal.hyderabad@ecoi.co.in 
Andhra Pradesh, 
Telangana, 
Yanam and  
part of Territory of UT of Pondicherry. 
JAIPUR - Smt. Sandhya Baliga 
Office of the Insurance Ombudsman, 
Jeevan Nidhi – II Bldg., Gr. Floor, 
Bhawani Singh Marg, 
Jaipur - 302 005. 
Tel.: 0141 - 2740363 
Email: Bimalokpal.jaiur@ecoi.co.in 
Rajasthan. 
ERNAKULAM - Ms. Poonam Bodra 
Office of the Insurance Ombudsman, 
2nd Floor, Pulinat Bldg., 
Opp. Cochin Shipyard, M. G. Road, 
Ernakulam - 682 015. 
Tel.: 0484 - 2358759 / 2359338 
Fax: 0484 - 2359336 
Email: bimalokpal.ernakulam@ecoi.co.in 
Kerala, UT of (a) Lakshadweep, (b) 
Mahe-a part of UT of Pondicherry. 
KOLKATA - Shri P. K. Rath 
Office of the Insurance Ombudsman, 
Hindustan Bldg. Annexe, 4th Floor,  
4, C.R. Avenue,  
West Bengal, 
Sikkim, 
UT of Andaman & Nicobar Islands. 
 
SBI General Insurance Company Limited                                   
                                                       
 
 
SBI General Insurance Company Limited Health Insurance Policy- Retail                     UIN: SBIHLIP21331V032021                  Page 33 of 45  
KOLKATA - 700 072.  
Tel.: 033 - 22124339 / 22124340  
Fax : 033 - 22124341 
Email: bimalokpal.kolkata@ecoi.co.in 
LUCKNOW -Shri Justice Anil Kumar Srvastava 
Office of the Insurance Ombudsman, 
6th Floor, Jeevan Bhawan, Phase-II, 
Nawal Kishore Road, Hazratganj,  
Lucknow - 226 001.  
Tel.: 0522 - 2231330 / 2231331 
Fax: 0522 - 2231310 
Email: bimalokpal.lucknow@ecoi.co.in 
Districts of Uttar Pradesh : 
Laitpur, Jhansi, Mahoba, Hamirpur, Banda, 
Chitrakoot, Allahabad, Mirzapur, Sonbhabdra, 
Fatehpur, Pratapgarh, Jaunpur,Varanasi, Gazipur, 
Jalaun, Kanpur, Lucknow, Unnao, Sitapur, 
Lakhimpur, Bahraich, Barabanki, Raebareli, 
Sravasti, Gonda, Faizabad, Amethi, Kaushambi, 
Balrampur, Basti, Ambedkarnagar, Sultanpur, 
Maharajgang, Santkabirnagar, Azamgarh, 
Kushinagar, Gorkhpur, Deoria, Mau, Ghazipur, 
Chandauli, Ballia, Sidharathnagar. 
MUMBAI - Shri Milind A. Kharat 
Office of the Insurance Ombudsman, 
3rd Floor, Jeevan SevaAnnexe,  
S. V. Road, Santacruz (W), 
Mumbai - 400 054. 
Tel.: 022 - 26106552 / 26106960 
Fax: 022 - 26106052 
Email: bimalokpal.mumbai@ecoi.co.in 
Goa,  
Mumbai Metropolitan Region  
excluding Navi Mumbai & Thane. 
NOIDA - Shri Chandra Shekhar Prasad 
Office of the Insurance Ombudsman, 
BhagwanSahai Palace  
4th Floor, Main Road, 
Naya Bans, Sector 15, 
Distt: Gautam Buddh Nagar, 
U.P-201301. 
Tel.: 0120-2514250 / 2514252 / 2514253 
Email: bimalokpal.noida@ecoi.co.in 
State of Uttaranchal and the following Districts of 
Uttar Pradesh: 
Agra, Aligarh, Bagpat, Bareilly, Bijnor, Budaun, 
Bulandshehar, Etah, Kanooj, Mainpuri, Mathura, 
Meerut, Moradabad, Muzaffarnagar, Oraiyya, 
Pilibhit, Etawah, Farrukhabad, Firozbad, 
Gautambodhanagar, Ghaziabad, Hardoi, 
Shahjahanpur, Hapur, Shamli, Rampur, Kashganj, 
Sambhal, Amroha, Hathras, Kanshiramnagar, 
Saharanpur. 
PATNA - Shri N. K. Singh 
Office of the Insurance Ombudsman, 
1st Floor,Kalpana Arcade Building,,  
Bazar Samiti Road, 
Bahadurpur, 
Patna 800 006. 
Tel.: 0612-2680952 
Email: bimalokpal.patna@ecoi.co.in 
Bihar, 
Jharkhand. 
PUNE - Shri Vinay Sah 
Office of the Insurance Ombudsman, 
Jeevan Darshan Bldg., 3rd Floor, 
C.T.S. No.s. 195 to 198, 
N.C. Kelkar Road, Narayan Peth, 
Pune – 411 030. 
Maharashtra, 
Area of Navi Mumbai and Thane 
excluding Mumbai Metropolitan Region. 
SBI General Insurance Company Limited                                   
Tel.: 020-41312555 
Email: bimalokpal.pune@ecoi.co.in 
Grievance may also be lodged at IRDAI Integrated Grievance Management System - https://igms.irda.gov.in/ 
STATUTORY NOTICE:  INSURANCE IS THE SUBJECT MATTER OF THE SOLICITATION 
UIN: SBIHLIP21331V032021                  
Page 34 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
ANNEXURE:  ENDORSEMENTS 
1. Removal of Room & ICU rent sub-limits:   
Notwithstanding anything contrary to it stated in the policy, It is hereby agreed and declared that insured having paid 
the premium to remove the limits prescribed on room and ICU rent the, Insurer shall pay the reasonable costs 
incurred during Hospitalisation subject to minimum 24hours Hospitalisation & covered illness or Accident during the 
policy period. 
All other terms and conditions will remain the same.  
The following exclusion appearing under the policy hereby stand deleted - 
Insurer shall pay the costs incurred during Hospitalisation subject to minimum 24hours Hospitalisation & covered 
illness or Accident during the policy period which would include the following: 
Room, Board & Nursing Charges as provided by the Hospital/Nursing Home Excluding registration and service 
Expenses: up to 1% of the Sum Insured per day. If admitted into Intensive Care Unit up to 2% of the Sum Insured per 
day.  In case the Insured opts for a higher room category, all incremental Expenses pertaining to room rent, Medical 
Practitioners / specialists fees and other incidental Expenses to be borne by the Insured. 
All admissible claims under Room, Board & Nursing Expenses including ICU, during the policy     
maximum up to 25% of the Sum Insured per illness/injury. 
2. Removal of sub-limits on operation and consultancy charges:   
period are restricted 
Notwithstanding anything contrary to it stated in the policy, It is hereby agreed and declared that insured having paid 
the premium to remove the limits prescribed on operation , consultancy and other such related charges, Insurer shall 
pay the reasonable costs incurred during Hospitalisation which would include the following: 
a. Medical Practitioner, Surgeon, Anaesthetist, Consultants, and Specialists Fees 
b. Anaesthesia, Blood, Oxygen, Operation Theatre Expenses, Surgical Appliances, Medicines & Drugs, Diagnostic 
Materials and X-ray, Dialysis, Chemotherapy, Radiotherapy, Cost of Pacemaker, prosthesis/internal implants 
and any medical Expenses incurred which is integral part of the operation 
All other terms and conditions will remain the same.  
The following exclusion appearing under the policy hereby stand deleted 
Medical Practitioner, Surgeon, Anaesthetist, Consultants, and Specialists Fees - All admissible claims under this 
section during the policy period restricted maximum up to 40% of the Sum Insured per illness/injury. 
Anaesthesia, Blood, Oxygen, Operation Theatre Expenses, Surgical Appliances, Medicines & Drugs, Diagnostic 
Materials and X-ray, Dialysis, Chemotherapy, Radiotherapy, Cost of Pacemaker, prosthesis/internal implants and any 
medical Expenses incurred which is integral part of the operation - All admissible claims under this section during the 
policy period restricted maximum up to 40% of the Sum Insured per illness/injury. 
3. Removal of Ayurvedic and homeopathic cover 
Notwithstanding anything contrary to it stated in the policy, It is hereby agreed and declared that insured having 
availed the discount in premium the policy excludes the expenses incurred on alternative medicines like ayurvedic, 
homeopathy, unani, acupuncture, acupressure, osteopath, naturopathy, chiropractic, reflexology and aromatherapy . 
All other terms and conditions will remain the same. 
UIN: SBIHLIP21331V032021                  
Page 35 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
Further following appearing in the scope of cover of the policy stand deleted - 
Ayurvedic Medicine: Ayurvedic Treatment covered up to maximum 15% of Sum Insured per Policy Period up to a 
maximum of Rs. 20000 subject to treatment taken at a Ayurvedic hospital confirming with our definition of hospital 
and which is registered with any of the local  Government bodies..  
Homeopathic and Unani system of medicine: Homeopathy and Unani Treatment covered up to maximum 10% of Sum 
Insured per Policy Period up to a maximum of Rs. 15000 subject to treatment taken at a Homeopathic / Unani 
hospital confirming with our definition of hospital and which is registered with any of the local  Government bodies. 
UIN: SBIHLIP21331V032021                  
Page 36 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
ANNEXURE A - DAY CARE LIST 
The following are the listed Day care procedures and such other Surgical Procedures that necessitate less than 24 
hours Hospitalisation due to medical/technological advancement / infrastructure facilities and the coverage of which 
is subject to the terms, conditions and exclusions of the policy 
Microsurgical operations on the middle ear  
1. Stapedectomy 
2. Revision of a stapedectomy 
3. Other operations on the auditory ossicles 
4. Myringoplasty (Type -I Tympanoplasty) 
5. Tympanoplasty (closure of an eardrum perforation/reconstruction of the auditory ossicles) 
6. Revision of a tympanoplasty 
7. Other microsurgical operations on the middle ear 
Other operations on the middle & internal ear 
8. Myringotomy 
9. Removal of a tympanic drain 
10. Incision of the mastoid process and middle ear 
11. Mastoidectomy 
12. Reconstruction of the middle ear 
13. Other excisions of the middle and inner ear 
14. Fenestration of the inner ear 
15. Revision of a fenestration of the inner ear 
16. Incision (opening) and destruction (elimination) of the inner ear 
17. Other operations on the middle and inner ear 
Operations on the nose & the nasal sinuses 
18. Excision and destruction of diseased tissue of the nose 
19. Operations on the turbinates (nasal concha) 
20. Other operations on the nose 
21. Nasal sinus aspiration 
Operations on the eyes 
22. Incision of tear glands 
23. Other operations on the tear ducts 
24. Incision of diseased eyelids 
25. Excision and destruction of diseased tissue of the eyelid 
26. Incision of diseased eyelids 
27. Operations on the canthus and epicanthus 
28. Corrective surgery for entropion and ectropion 
29. Corrective surgery for blepharoptosis 
30. Removal of a foreign body from the conjunctiva 
UIN: SBIHLIP21331V032021                  
Page 37 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
31. Removal of a foreign body from the cornea 
32. Incision of the cornea 
33. Operations for pterygium 
34. Other operations on the cornea 
35. Removal of a foreign body from the lens of the eye 
36. Removal of a foreign body from the posterior chamber of the eye 
37. Removal of a foreign body from the orbit and eyeball 
38. Operation of cataract 
Operations on the skin & subcutaneous tissues 
39. Incision of a pilonidal sinus 
40. Other incisions of the skin and subcutaneous tissues 
41. Surgical wound toilet (wound debridement) and removal of diseased tissue of the skin and subcutaneous 
tissues 
42. Local excision of diseased tissue of the skin and subcutaneous tissues 
43. Other excisions of the skin and subcutaneous tissues 
44. Simple restoration of surface continuity of the skin and subcutaneous tissues 
45. Free skin transplantation, donor site 
46. Free skin transplantation, recipient site 
47. Revision of skin plasty 
48. Other restoration and reconstruction of the skin and subcutaneous tissues 
49. Chemosurgery to the skin 
50. Destruction of diseased tissue in the skin and subcutaneous tissues 
Operations on the tongue 
51. Incision, excision and destruction of diseased tissue of the tongue 
52. Partial glossectomy 
53. Glossectomy 
54. Reconstruction of the tongue 
55. Other operations on the tongue 
Operations on the salivary glands & salivary ducts 
56. Incision and lancing of a salivary gland and a salivary duct 
57. Excision of diseased tissue of a salivary gland and a salivary duct 
58. Resection of a salivary gland 
59. Reconstruction of a salivary gland and a salivary duct 
60. Other operations on the salivary glands and salivary ducts 
Other operations on the mouth & face 
61. External incision and drainage in the region of the mouth, jaw and face 
62. Incision of the hard and soft palate 
63. Excision and destruction of diseased hard and soft palate 
UIN: SBIHLIP21331V032021                  
Page 38 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
64. Incision, excision and destruction in the mouth 
65. Plastic surgery to the floor of the mouth 
66. Palatoplasty 
67. Other operations in the mouth 
Operations on the tonsils & adenoids 
68. Transoral incision and drainage of a pharyngeal abscess 
69. Tonsillectomy without adenoidectomy 
70. Tonsillectomy with adenoidectomy 
71. Excision and destruction of a lingual tonsil 
72. Other operations on the tonsils and adenoids 
Trauma surgery and orthopaedics 
73. Incision on bone, septic and aseptic 
74. Closed reduction on fracture, luxation or epiphyseolysis with osteosynthesis 
75. Suture and other operations on tendons and tendon sheath 
76. Reduction of dislocation under GA 
77. Arthroscopic knee aspiration 
Operations on the breast 
78. Incision of the breast 
79. Operations on the nipple 
Operations on the digestive tract 
80. Incision and excision of tissue in the perianal region 
81. Surgical treatment of anal fistulas 
82. Surgical treatment of haemorrhoids 
83. Division of the anal sphincter (sphincterotomy) 
84. Other operations on the anus 
85. Ultrasound guided aspirations 
86. Sclerotherapy etc. 
87. Laparoscopic cholecystectomy 
Operations on the female sexual organs 
88. Incision of the ovary 
89. Insufflation of the Fallopian tubes 
90. Other operations on the Fallopian tube 
91. Dilatation of the cervical canal 
92. Conisation of the uterine cervix 
93. Other operations on the uterine cervix 
94. Incision of the uterus (hysterotomy) 
95. Therapeutic curettage 
UIN: SBIHLIP21331V032021                  
Page 39 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
96. Culdotomy 
97. Incision of the vagina 
98. Local excision and destruction of diseased tissue of the vagina and the pouch of Douglas 
99. Incision of the vulva  
100. Operations on Bartholin’s glands (cyst) 
Operations on the prostate & seminal vesicles 
101. Incision of the prostate 
102. Transurethral excision and destruction of prostate tissue 
103. Transurethral and percutaneous destruction of prostate tissue 
104. Open surgical excision and destruction of prostate tissue 
105. Radical prostatovesiculectomy 
106. Other excision and destruction of prostate tissue 
107. Operations on the seminal vesicles 
108. Incision and excision of periprostatic tissue 
109. Other operations on the prostate 
Operations on the scrotum & tunica vaginalis testis 
110. Incision of the scrotum and tunica vaginalis testis 
111. Operation on a testicular hydrocele 
112. Excision and destruction of diseased scrotal tissue 
113. Plastic reconstruction of the scrotum and tunica vaginalis testis 
114. Other operations on the scrotum and tunica vaginalis testis 
Operations on the testes 
115. Incision of the testes 
116. Excision and destruction of diseased tissue of the testes 
117. Unilateral orchidectomy 
118. Bilateral orchidectomy 
119. Orchidopexy 
120. Abdominal exploration in cryptorchidism 
121. Surgical repositioning of an abdominal testis 
122. Reconstruction of the testis 
123. Implantation, exchange and removal of a testicular prosthesis 
124. Other operations on the penis 
Operations on the spermatic cord, epididymis und ductus deferens 
125. Surgical treatment of a varicocele and a hydrocele of the spermatic cord 
126. Excision in the area of the epididymis 
127. Epididymectomy 
128. Reconstruction of the spermatic cord 
129. Reconstruction of the ductus deferens and epididymis 
130. Other operations on the spermatic cord, epididymis and ductus deferens 
UIN: SBIHLIP21331V032021                  
Page 40 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
Operations on the penis 
131. Operations on the foreskin 
132. Local excision and destruction of diseased tissue of the penis 
133. Amputation of the penis 
134. Plastic reconstruction of the penis 
135. Other operations on the penis 
Operations on the urinary system 
136. Cystoscopical removal of stones 
Other Operations 
137. Lithotripsy 
138. Coronary angiography 
139. Haemodialysis 
140. Radiotherapy for Cancer 
141. Cancer Chemotherapy 
UIN: SBIHLIP21331V032021                  
Page 41 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
Item 
List I — Items for which coverage is not available in the policy  
SI 
No 
1 
BABY FOOD 
2 
BABY UTILITIES CHARGES 
3 
BEAUTY SERVICES 
4 
BELTS/ BRACES 
5 
BUDS 
6 
COLD PACK/HOT PACK 
7 
CARRY BAGS 
8 
EMAIL / INTERNET CHARGES 
9 
10 
FOOD CHARGES OTHER THAN PATIENT's DIET PROVIDED BY HOSPITAL 
LEGGINGS 
11 
12 
LAUNDRY CHARGES 
MINERAL WATER 
13 
14 
SANITARY PAD 
TELEPHONE CHARGES 
15 
16 
GUEST SERVICES 
CREPE BANDAGE 
17 
18 
DIAPER OF ANY TYPE 
EYELET COLLAR 
19 
20 
SLINGS 
BLOOD GROUPING AND CROSS MATCHING OF DONORS SAMPLES 
21 
22 
SERVICE CHARGES WHERE NURSING CHARGE ALSO CHARGED 
Television Char es 
23 
24 
EXTRA DIET OF PATIENT (OTHER THAN THAT WHICH FORMS PART OF BED CHARGE 
SURCHARGES 
ATTENDANT CHARGES 
25 
26 
27 
BIRTH CERTIFICATE 
CERTIFICATE CHARGES 
28 
29 
COURIER CHARGES 
CONVEYANCE CHARGES 
30 
31 
MEDICAL CERTIFICATE 
MEDICAL RECORDS 
32 
33 
PHOTOCOPIES CHARGES 
MORTUARY CHARGES 
34 
35 
WALKING AIDS CHARGES 
OXYGEN CYLINDER FOR USAGE OUTSIDE THE HOSPITAL 
36 
37 
NEBULIZER KIT 
SPACER 
SPIROMETRE 
38 
UIN: SBIHLIP21331V032021                  
Page 42 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
39 
40 
STEAM INHALER 
ARMSLING 
41 
42 
THERMOMETER 
CERVICAL COLLAR 
43 
44 
SPLINT 
DIABETIC FOOTWEAR 
45 
46 
KNEE BRACES LONG/ SHORT/ HINGED 
KNEE IMMOBILIZER/SHOULDER IMMOBILIZER 
47 
48 
LUMBO SACRAL BELT 
NIMBUS BED OR WATER OR AIR BED CHARGES 
49 
50 
AMBULANCE COLLAR 
AMBULANCE EQUIPMENT 
51 
52 
ABDOMINAL BINDER 
PRIVATE NURSES CHARGES- SPECIAL NURSING CHARGES 
53 
54 
SUGAR FREE Tablets 
CREAMS POWDERS LOTIONS (Toiletries are not payable, only prescribed medical pharmaceuticals 
payable 
55 
56 
ECG ELECTRODES 
GLOVES 
57 
58 
NEBULISATION KIT 
ANY KIT WITH NO DETAILS MENTIONED [DELIVERY KIT, ORTHOKIT, RECOVERY KIT, ETC 
59 
60 
KIDNEY TRAY 
MASK 
61 
62 
OUNCE GLASS 
OXYGEN MASK 
63 
64 
PELVIC TRACTION BELT 
PAN CAN 
65 
66 
TROLLY COVER 
UROMETER, URINE JUG 
67 
68 
Item 
AMBULANCE 
VASOFIX SAFETY 
List II— Items that are to be subsumed into Room charges  
No. 
1 
BABY CHARGES UNLESS SPECIFIED/INDICATED 
2 
HAND WASH 
3 
SHOE COVER 
4 
CAPS 
5 
CRADLE CHARGES 
6 
COMB 
7 
EAU-DE-COLOGNE / ROOM FRESHNERS 
8 
FOOT COVER 
9 
GOWN 
SLIPPERS 
10 
UIN: SBIHLIP21331V032021                  
Page 43 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
11 
TISSUE PAPER 
TOOTH PASTE 
12 
13 
TOOTH BRUSH 
BED PAN 
14 
15 
FACE MASK 
FLEXI MASK 
16 
17 
HAND HOLDER 
SPUTUM CUP 
18 
19 
DISINFECTANT LOTIONS 
LUXURY TAX 
20 
21 
HVAC 
HOUSE KEEPING CHARGES 
22 
23 
AIR CONDITIONER CHARGES 
1M IV INJECTION CHARGES 
24 
25 
CLEAN SHEET 
BLANKET/VVARMER BLANKET 
26 
27 
ADMISSION KIT 
DIABETIC CHART CHARGES 
28 
29 
DOCUMENTATION CHARGES / ADMINISTRATIVE EXPENSES 
DISCHARGE PROCEDURE CHARGES 
30 
31 
DAILY CHART CHARGES 
ENTRANCE PASS / VISITORS PASS CHARGES 
32 
33 
EXPENSES RELATED TO PRESCRIPTION ON DISCHARGE 
FILE OPENING CHARGES 
34 
35 
INCIDENTAL EXPENSES / MISC. CHARGES NOT EXPLAINED 
PATIENT IDENTIFICATION BAND / NAME TAG 
36 
37 
PULSEOXYMETER CHARGES 
List III - Items that are to be subsumed into Procedure Charges 
Item 
No. 
1 
2 
HAIR REMOVAL CREAM 
DISPOSABLES RAZORS CHARGES (for site preparations) 
3 
4 
EYE PAD 
EYE SHEILD 
5 
6 
CAMERA COVER 
DVD, CD CHARGES 
7 
8 
CAUSE SOFT 
GAUZE 
9 
10 
WARD AND THEATRE BOOKING CHARGES 
ARTHROSCOPY AND ENDOSCOPY INSTRUMENTS 
11 
12 
SURGICAL DRILL 
MICROSCOPE COVER 
SURGICAL BLADES, HARMONICSCALPEL, SHAVER 
13 
UIN: SBIHLIP21331V032021                  
Page 44 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     
SBI General Insurance Company Limited                                   
14 
15 
EYE KIT 
EYE DRAPE 
16 
17 
X-RAY FILM 
BOYLES APPARATUS CHARGES 
18 
19 
COTTON 
COTTON BANDAGE 
20 
21 
SURGICAL TAPE 
APRON 
22 
23 
TORNIQUET 
ORTHOBUNDLE, GYNAEC BUNDLE 
Item 
List IV — Items that are to be subsumed into costs of treatment 
No. 
ADMISSION/REGISTRATION CHARGES 
2 
HOSPITALISATION FOR EVALUATION/ DIAGNOSTIC PURPOSE 
3 
URINE CONTAINER 
4 
BLOOD RESERVATION CHARGES AND ANTE NATAL BOOKING CHARGES 
5 
BIPAP MACHINE 
6 
CPAP/ CAPD EQUIPMENTS 
7 
INFUSION PUMP- COST 
8 
HYDROGEN PEROXIDE/SPIRIT/DISINFECTANTS ETC 
9 
10 
NUTRITION PLANNING CHARGES - DIETICIAN CHARGES- DIET CHARGES 
HIV KIT 
UIN: SBIHLIP21331V032021                  
Page 45 of 45  
SBI General Insurance Company Limited Health Insurance Policy- Retail                     """
    

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