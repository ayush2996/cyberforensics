# workflow.py
from llm_manager import llm
from crime_classifier import crime_classifier
from correlation_engine import correlation_engine
from models import CrimeType, QuestionResponse, ReportResponse, CorrelationResult
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class EnhancedCyberWorkflow:
    """
    Enhanced cyber crime reporting workflow with:
    - Crime type classification
    - Interactive questioning based on crime type
    - JSON schema-based report generation
    - Correlation analysis with previous cases
    """
    
    def __init__(self):
        self.llm = llm
        self.crime_classifier = crime_classifier
        self.correlation_engine = correlation_engine
        self.case_id = str(uuid.uuid4())[:8]
    
    async def process_incident(self, description: str) -> Dict[str, Any]:
        """
        Main workflow: Classify  Question  Report  Correlate
        
        Args:
            description: Initial incident description
            
        Returns:
            Response with crime type selection and next steps
        """
        # Step 1: Classify the crime
        crime_type_response = self.crime_classifier.classify_incident(description)
        
        return {
            "status": "crime_type_selected",
            "detected_types": [ct.value for ct in crime_type_response.detected_types],
            "recommendation": crime_type_response.recommendation.value,
            "confidence": crime_type_response.confidence,
            "message": crime_type_response.message,
            "case_id": self.case_id
        }
    
    async def generate_questions(self, description: str, 
                                 crime_type: CrimeType) -> QuestionResponse:
        """
        Generate crime-type-specific clarifying questions
        
        Args:
            description: Incident description
            crime_type: Detected crime type
            
        Returns:
            QuestionResponse with tailored questions
        """
        from prompts import (
            PHISHING_QUESTIONS_PROMPT,
            RANSOMWARE_QUESTIONS_PROMPT,
            DATA_BREACH_QUESTIONS_PROMPT,
            IDENTITY_THEFT_QUESTIONS_PROMPT,
            FRAUD_QUESTIONS_PROMPT,
            MALWARE_QUESTIONS_PROMPT,
            DDOS_QUESTIONS_PROMPT,
            HACKING_QUESTIONS_PROMPT,
            EXTORTION_QUESTIONS_PROMPT,
            SPAM_QUESTIONS_PROMPT
        )
        
        prompt_map = {
            CrimeType.PHISHING: PHISHING_QUESTIONS_PROMPT,
            CrimeType.RANSOMWARE: RANSOMWARE_QUESTIONS_PROMPT,
            CrimeType.DATA_BREACH: DATA_BREACH_QUESTIONS_PROMPT,
            CrimeType.IDENTITY_THEFT: IDENTITY_THEFT_QUESTIONS_PROMPT,
            CrimeType.FRAUD: FRAUD_QUESTIONS_PROMPT,
            CrimeType.MALWARE: MALWARE_QUESTIONS_PROMPT,
            CrimeType.DDoS: DDOS_QUESTIONS_PROMPT,
            CrimeType.HACKING: HACKING_QUESTIONS_PROMPT,
            CrimeType.EXTORTION: EXTORTION_QUESTIONS_PROMPT,
            CrimeType.SPAM: SPAM_QUESTIONS_PROMPT,
        }
        
        try:
            prompt_template = prompt_map.get(crime_type, FRAUD_QUESTIONS_PROMPT)
            prompt = prompt_template.format(description=description)
            
            system_prompt = "You are a cybercrime investigator generating specific, targeted questions. Respond ONLY with a JSON array of questions, no other text."
            
            response = self.llm.generate(prompt, system_prompt, max_tokens=800)
            
            # Parse questions
            questions = json.loads(response)
            
            return QuestionResponse(
                status="needs_clarification",
                questions=questions,
                confidence=0.8,
                crime_type=crime_type
            )
        
        except Exception as e:
            print(f"Error generating questions: {e}")
            return QuestionResponse(
                status="needs_clarification",
                questions=["Can you provide more details about the incident?"],
                confidence=0.5,
                crime_type=crime_type
            )
    
    async def generate_report(self, description: str, 
                             crime_type: CrimeType,
                             answered_questions: Dict[str, str]) -> ReportResponse:
        """
        Generate professional crime report with JSON schema
        
        Args:
            description: Original incident description
            crime_type: Classification of crime
            answered_questions: User's answers to clarifying questions
            
        Returns:
            ReportResponse with structured report data
        """
        try:
            # Get crime-specific model
            report_model = crime_classifier.get_crime_model(crime_type)
            
            # Build prompt to fill the schema
            incident_summary = f"""
Original Report: {description}

Follow-up Answers:
{json.dumps(answered_questions, indent=2)}
"""
            
            prompt = f"""
You are a professional cybercrime analyst. Based on the incident details provided, generate a comprehensive report in JSON format that strictly follows this schema:

Crime Type: {crime_type.value}

Incident Details:
{incident_summary}

Analyze the incident and generate a detailed JSON report. Ensure ALL required fields are filled with appropriate values.
The report should be valid JSON following the criminal report schema for {crime_type.value} crimes.

Return ONLY valid JSON, no markdown, no explanation, JUST the JSON object.
"""
            
            system_prompt = f"""You are an expert cybercrime report analyst specializing in {crime_type.value} investigations.
Generate professional, detailed reports in pristine JSON format.
CRITICAL: Return ONLY the JSON object, no markdown code blocks, no explanations, just valid JSON."""
            
            response = self.llm.generate(prompt, system_prompt, max_tokens=2000)
            
            # Parse and validate the report
            report_data = json.loads(response)
            
            # Perform correlation analysis
            correlation_result = await self.correlation_engine.analyze_correlation(
                report_data, crime_type
            )
            
            return ReportResponse(
                status="success",
                report_data=report_data,
                crime_type=crime_type,
                confidence=0.9,
                correlation_analysis=correlation_result
            )
        
        except json.JSONDecodeError as e:
            print(f"Error parsing report JSON: {e}")
            # Try to extract data anyway
            return ReportResponse(
                status="partial_success",
                report_data={"error": "Report generation incomplete", "raw_response": str(e)},
                crime_type=crime_type,
                confidence=0.5,
                correlation_analysis=CorrelationResult()
            )
        except Exception as e:
            print(f"Error generating report: {e}")
            return ReportResponse(
                status="error",
                report_data={"error": str(e)},
                crime_type=crime_type,
                confidence=0.0,
                correlation_analysis=CorrelationResult()
            )
    
    async def analyze_correlations(self, report_data: Dict[str, Any],
                                   crime_type: CrimeType) -> CorrelationResult:
        """
        Analyze incident for correlations with previous cases
        
        Args:
            report_data: Structured incident report
            crime_type: Type of crime
            
        Returns:
            Correlation analysis results
        """
        return await self.correlation_engine.analyze_correlation(
            report_data, crime_type
        )
    
    def register_case(self, report_data: Dict[str, Any], case_id: str):
        """Register completed case in correlation database"""
        self.correlation_engine.add_case_to_database(report_data, case_id)
    
    async def interactive_interview(self, description: str) -> Dict[str, Any]:
        """
        Complete interactive interview flow
        
        Args:
            description: Initial incident description
            
        Returns:
            Complete case information with report
        """
        # Step 1: Classify
        classification = await self.process_incident(description)
        
        if classification["status"] != "crime_type_selected":
            return classification
        
        crime_type = CrimeType(classification["recommendation"])
        
        # Step 2: Generate questions
        questions_response = await self.generate_questions(description, crime_type)
        
        return {
            "step": "ask_questions",
            "case_id": classification["case_id"],
            "crime_type": crime_type.value,
            "questions": questions_response.questions
        }
    
    async def submit_answers_and_generate_report(self, 
                                                description: str,
                                                crime_type_str: str,
                                                answers: Dict[str, str],
                                                case_id: str) -> ReportResponse:
        """
        Process user answers and generate final report
        
        Args:
            description: Original incident description
            crime_type_str: String representation of crime type
            answers: User's answers to questions
            case_id: Case identifier
            
        Returns:
            Complete report with correlation analysis
        """
        crime_type = CrimeType(crime_type_str)
        
        # Generate the report
        report = await self.generate_report(description, crime_type, answers)
        
        if report.status == "success":
            # Register in database
            self.register_case(report.report_data, case_id)
        
        return report

# Export singleton instance
workflow = EnhancedCyberWorkflow()

