import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from datetime import datetime
from io import BytesIO
from fastapi import UploadFile
from typing import List

class GeminiService:
    def __init__(self):
        api_key = "AIzaSyCClaQFo9MrwLwbhv1ryZ21neeQbEyN41A" #os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def _extract_pdf_text(self, file: UploadFile, max_pages: int = 5) -> str:
        # Read the uploaded file into memory
        contents = await file.read()
        pdf_stream = BytesIO(contents)
        
        reader = PdfReader(pdf_stream)
        if reader.is_encrypted:
            reader.decrypt("")
        text = "\n\n".join([page.extract_text() for page in reader.pages[:max_pages]])
        
        # Reset file pointer for potential future reads
        await file.seek(0)
        return text

    async def evaluate_full_claim(self, policy_file: UploadFile, discharge_file: UploadFile, bill_file: UploadFile) -> dict:
        """Evaluates a full claim based on policy, discharge summary, and medical bill."""
        try:
            # Validate file types
            for file in [policy_file, discharge_file, bill_file]:
                if not file.filename.lower().endswith('.pdf'):
                    raise ValueError(f"File {file.filename} must be a PDF")

            # Extract text from all documents
            policy_text = await self._extract_pdf_text(policy_file)
            discharge_text = await self._extract_pdf_text(discharge_file)
            bill_text = await self._extract_pdf_text(bill_file)
            
            prompt = """
            You are a health insurance claim expert.

            Three documents are provided:
            1. Insurance policy:
            {policy_text}

            2. Discharge summary:
            {discharge_text}

            3. Medical bill:
            {bill_text}

            Your tasks:
            - Carefully read the documents.
            - Based on the policy terms, exclusions, and limits, calculate the **total claimable amount**.
            - Ignore any costs not covered (e.g. non-medical items, limits).
            - Give a detailed breakdown of reasoning.

            You MUST respond in EXACTLY this format with both lines:
            ---
            ✅ Final Claimable Amount: ₹<amount>
            🧠 Reasoning: <detailed explanation of what is covered, what is not, and why>
            ---
            """.format(
                policy_text=policy_text,
                discharge_text=discharge_text,
                bill_text=bill_text
            )

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # More robust parsing of the response
            try:
                # Split by newlines and remove empty lines
                lines = [line.strip() for line in response_text.split('\n') if line.strip()]
                
                # Find the amount line and reasoning line
                amount_line = next(line for line in lines if '₹' in line)
                reasoning_line = next(line for line in lines if 'Reasoning:' in line or '🧠' in line)
                
                # Extract amount and reasoning
                claimable_amount = float(amount_line.split('₹')[1].strip().replace(',', ''))
                reasoning = reasoning_line.split('Reasoning:' if 'Reasoning:' in reasoning_line else '🧠')[1].strip()
                
                if not reasoning:
                    reasoning = "Unable to extract reasoning from the response. Please try again."

                return {
                    "claimable_amount": claimable_amount,
                    "reasoning": reasoning,
                    "timestamp": datetime.now()
                }
            except Exception as parse_error:
                # If parsing fails, return the raw response as reasoning
                return {
                    "claimable_amount": 0,
                    "reasoning": f"Error parsing response. Raw response: {response_text}",
                    "timestamp": datetime.now()
                }

        except Exception as e:
            raise Exception(f"Error evaluating full claim: {str(e)}")

    async def validate_medical_report(self, file: UploadFile) -> dict:
        """Validates if the uploaded file is a valid medical report."""
        try:
            if not file.filename.lower().endswith('.pdf'):
                raise ValueError("Uploaded file must be a PDF")

            policy_text = await self._extract_pdf_text(file)
            
            prompt = """
            You are a medical document classification expert.

            Check the uploaded PDF and answer:

            Is this document a **valid medical report or discharge summary**?

            Only evaluate based on structure, medical terminology, and presence of sections like patient details, diagnosis, treatment, hospital, dates, etc.

            Return your answer strictly in this format:

            ---
            ✅ Is Medical Report: Yes / No
            🧠 Reason: <brief reason explaining how you identified it>
            ---
            """

            response = self.model.generate_content([prompt, policy_text])
            response_text = response.text.strip()

            # Parse the response
            lines = response_text.split('\n')
            is_valid = "Yes" in lines[1].split(':')[1].strip()
            reason = lines[2].split('Reason:')[1].strip()

            return {
                "is_valid_report": is_valid,
                "reason": reason,
                "timestamp": datetime.now()
            }

        except Exception as e:
            raise Exception(f"Error validating medical report: {str(e)}")

    async def generate_quick_claim(self, file: UploadFile, sum_insured: float, 
                           event_start: str, event_end: str, hospital_cost: float) -> dict:
        try:
            if not file.filename.lower().endswith('.pdf'):
                raise ValueError("Uploaded file must be a PDF")

            policy_text = await self._extract_pdf_text(file)
            
            prompt = f"""
            You are a health insurance claim expert.

            Here's the scenario:
            - The patient had a cardiac event from {event_start} to {event_end}.
            - The sum insured under their policy is ₹{sum_insured}.
            - The average hospital treatment cost for this case is ₹{hospital_cost}.

            Below is the insurance policy document. Based on the conditions, coverage limits, exclusions, sub-limits, and caps from this policy:

            1. Calculate how much can actually be **claimed** for this cardiac event which is a heart disease. This could be less than sum insured if there are caps (e.g., room rent limit, disease-specific caps, ICU % limit).
            2. Then return **40% of the final claimable amount** as the **Quick Claim** (this is the emergency payout given upfront).

            Policy Document:
            {policy_text}

            Respond ONLY in this format:

            ---
            ✅ Claimable Amount: ₹<calculated based on policy>
            ⚡ Quick Claim (40%): ₹<40% of above>
            🧠 Reason: <how you arrived at that claimable amount, based on the policy>
            ---
            """

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Parse the response to extract amounts and reason
            lines = response_text.split('\n')
            claimable_amount = float(lines[1].split('₹')[1].strip().replace(',', ''))
            quick_claim_amount = float(lines[2].split('₹')[1].strip().replace(',', ''))
            reason = lines[3].split('Reason:')[1].strip()

            return {
                "claimable_amount": claimable_amount,
                "quick_claim_amount": quick_claim_amount,
                "reason": reason,
                "timestamp": datetime.now()
            }

        except Exception as e:
            raise Exception(f"Error generating quick claim: {str(e)}")

    def generate_claim_analysis(self, policy_text: str, claim_details: dict) -> dict:
        prompt = self._create_prompt(policy_text, claim_details)
        response = self.model.generate_content(prompt)
        return self._parse_response(response.text.strip())

    def _create_prompt(self, policy_text: str, claim_details: dict) -> str:
        bpm_str = f"- The patient's heart rate (bpm) during the event was {claim_details['bpm']}.\n" if 'bpm' in claim_details else ""
        timestamp_str = f"- The event occurred at {claim_details['event_start']}.\n" if 'event_start' in claim_details else ""
        return f"""
        You are a health insurance claim expert.

        Here's the scenario:
        {timestamp_str}{bpm_str}- The sum insured under their policy is ₹{claim_details['sum_insured']}.
        - The average hospital treatment cost for this case is ₹{claim_details['hospital_cost']}.

        Below is the insurance policy document. Based on the conditions, coverage limits, exclusions, sub-limits, and caps from this policy:

        1. Calculate how much can actually be **claimed** for this cardiac event which is a heart disease. This could be less than sum insured if there are caps (e.g., room rent limit, disease-specific caps, ICU % limit).
        2. Then return **40% of the final claimable amount** as the **Quick Claim** (this is the emergency payout given upfront).

        Policy Document:
        {policy_text}

        Respond ONLY in this format:

        ---
        ✅ Claimable Amount: ₹<calculated based on policy>
        ⚡ Quick Claim (40%): ₹<40% of above>
        🧠 Reason: <how you arrived at that claimable amount, based on the policy>
        ---
        """

    def _parse_response(self, response_text: str) -> dict:
        lines = response_text.split('\n')
        return {
            'claimable_amount': float(lines[1].split('₹')[1].replace(',', '')),
            'quick_claim_amount': float(lines[2].split('₹')[1].replace(',', '')),
            'reason': lines[3].split('Reason: ')[1]
        } 