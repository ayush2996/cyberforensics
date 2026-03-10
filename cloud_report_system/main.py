from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from workflow import workflow
from crime_classifier_v3 import crime_classifier_v3
from self_rag import self_rag
from expert_analyzer import expert_analyzer
from corrective_rag import corrective_rag
from models import (
    CrimeTypeSelectionRequest, 
    CrimeTypeSelectionResponse,
    ReportRequest,
    QuestionResponse,
    ReportResponse,
    CorrelationResult,
    CrimeType
)
from typing import Dict, Any
import json
import numpy as np
from fastapi.responses import JSONResponse

# ===================== NUMPY-SAFE JSON HELPER =====================
def sanitize(obj):
    """Recursively convert numpy types to native Python for JSON serialization."""
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize(i) for i in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

# ===================== INITIALIZE APP =====================
app = FastAPI(
    title="Enhanced Cyber Crime Report System",
    description="AI-powered cyber crime reporting with crime type selection, intelligent questions, and correlation detection",
    version="2.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage (in production, use database)
active_sessions = {}

# ===================== ROOT & HEALTH ENDPOINTS =====================
@app.get("/")
def home():
    return {
        "message": "Enhanced Cyber Crime Report System API",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "start_report": "/api/v1/start-report",
            "classify_crime": "/api/v1/classify-crime",
            "get_questions": "/api/v1/get-questions",
            "submit_report": "/api/v1/submit-report",
            "get_crime_types": "/api/v1/crime-types",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "providers": ["Groq LLM", "Cohere Embeddings"],
        "features": [
            "Crime type classification",
            "Interactive questioning",
            "JSON schema reports",
            "Correlation analysis"
        ]
    }

# ===================== CRIME TYPE ENDPOINTS =====================
@app.get("/api/v1/crime-types")
def get_supported_crime_types():
    """Get list of supported cyber crime types"""
    return {
        "status": "success",
        "crime_types": [
            {
                "id": crime_type.value,
                "name": crime_type.value.replace("_", " ").title(),
                "description": get_crime_description(crime_type)
            }
            for crime_type in CrimeType
        ],
        "total": len(list(CrimeType))
    }

def get_crime_description(crime_type: CrimeType) -> str:
    """Get description for crime type"""
    descriptions = {
        CrimeType.PHISHING: "Deceptive emails or messages to steal credentials",
        CrimeType.RANSOMWARE: "Encryption of data with ransom demands",
        CrimeType.DATA_BREACH: "Unauthorized access to confidential data",
        CrimeType.IDENTITY_THEFT: "Unauthorized use of someone's identity",
        CrimeType.FRAUD: "Deceptive financial schemes",
        CrimeType.MALWARE: "Malicious software infections",
        CrimeType.DDoS: "Distributed denial of service attacks",
        CrimeType.HACKING: "Unauthorized access to systems",
        CrimeType.EXTORTION: "Threats demanding payment or action",
        CrimeType.SPAM: "Unwanted unsolicited messages"
    }
    return descriptions.get(crime_type, "Cyber crime incident")

# ===================== WORKFLOW ENDPOINTS =====================
@app.post("/api/v1/start-report", response_model=Dict[str, Any])
async def start_report(request: CrimeTypeSelectionRequest):
    """
    Start a new incident report - classify the crime type
    
    Request body:
    {
        "description": "Brief description of the incident"
    }
    
    Returns case ID and initial classification
    """
    try:
        print(f"\n Starting new report...")
        print(f"   Description: {request.description[:100]}...")
        
        # Process incident
        response = await workflow.process_incident(request.description)
        
        # Store session
        case_id = response["case_id"]
        active_sessions[case_id] = {
            "description": request.description,
            "crime_type": response["recommendation"],
            "step": "classification_complete"
        }
        
        print(f"[OK] Crime type classified: {response['recommendation']}")
        return response
    
    except Exception as e:
        print(f"[ERROR] Error in start_report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/classify-crime")
async def classify_crime(request: CrimeTypeSelectionRequest) -> Dict[str, Any]:
    """
    Classify an incident into cyber crime categories
    
    Uses advanced 4-stage AI classifier:
    1. Semantic Router (embedding-based)
    2. Hierarchical Taxonomy
    3. Pattern Matching
    4. RAG Validation
    
    Returns full pipeline results with confidence metrics
    """
    try:
        print(f"\n[*] Classifying incident with 4-stage pipeline...")
        
        # Run multi-stage classification
        classification_result = await crime_classifier_v3.classify_incident(
            request.description,
            include_reasoning=True
        )
        
        # Run self-RAG validation
        validation_result = await self_rag.validate_prediction(
            classification_result['final_prediction'],
            classification_result['final_confidence'],
            classification_result['stages'],
            request.description
        )
        
        # Check if expert review needed
        expert_flag = await expert_analyzer.analyze_for_flagging(
            classification_result,
            request.description,
            classification_result['stages']
        )
        
        # Build response
        response = {
            "status": "success",
            "case_id": f"case_{hash(request.description) % 10000000}",
            "incident_description": classification_result['incident_description'],
            "final_prediction": classification_result['final_prediction'],
            "final_confidence": classification_result['final_confidence'],
            "submission_status": classification_result['submission_status'],
            "stages": classification_result['stages'],
            "stage_scores": classification_result['stage_scores'],
            "validation_metrics": classification_result['validation_metrics'],
            "self_rag_validation": {
                "checkpoints_passed": validation_result.get('checkpoints_passed', 0),
                "total_checkpoints": validation_result.get('total_checkpoints', 5),
                "adjusted_confidence": validation_result.get('adjusted_confidence', classification_result['final_confidence']),
                "recommendation": validation_result.get('recommendation', 'SUBMIT'),
                "checkpoint_details": validation_result.get('checkpoint_details', [])
            },
            "expert_flagging": {
               "flagged": expert_flag is not None,
               "flag_reason": expert_flag.reason.value if expert_flag else None,
               "severity": expert_flag.severity if expert_flag else None
            },
            "reasoning": classification_result['reasoning'],
            "message": f"Crime type '{classification_result['final_prediction']}' detected with {classification_result['final_confidence']:.1%} confidence"
        }
        
        print(f"[OK] Classification complete: {classification_result['final_prediction']} ({classification_result['final_confidence']:.1%})")
        return JSONResponse(content=sanitize(response))
    
    except Exception as e:
        print(f"[ERROR] Error in classify_crime: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/get-questions")
async def get_clarifying_questions(
    description: str,
    crime_type: str,
    case_id: str
) -> QuestionResponse:
    """
    Get crime-type-specific clarifying questions
    
    Query parameters:
    - description: Original incident description
    - crime_type: Detected crime type (e.g., 'phishing')
    - case_id: Case identifier from start-report
    """
    try:
        print(f"\n Generating questions for {crime_type}...")
        
        crime_type_enum = CrimeType(crime_type)
        
        # Update session
        if case_id in active_sessions:
            active_sessions[case_id]["step"] = "questions_generated"
        
        questions_response = await workflow.generate_questions(
            description, 
            crime_type_enum
        )
        
        print(f" Generated {len(questions_response.questions)} questions")
        return questions_response
    
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid crime type: {crime_type}")
    except Exception as e:
        print(f" Error in get_questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class SubmitReportRequest(ReportRequest):
    """Extended request with answers"""
    crime_type: str
    case_id: str
    answers: Dict[str, str]

@app.post("/api/v1/submit-report", response_model=ReportResponse)
async def submit_report(request: SubmitReportRequest) -> ReportResponse:
    """
    Submit answers and generate professional crime report
    
    Request body:
    {
        "user_input": "Original incident description",
        "crime_type": "phishing",
        "case_id": "abc12345",
        "answers": {
            "Question 1": "Answer 1",
            "Question 2": "Answer 2"
        }
    }
    
    Returns:
    - Structured JSON report for the specific crime type
    - Confidence score
    - Correlation analysis with previous cases
    - Recommendations
    """
    try:
        print(f"\n Generating report for case {request.case_id}...")
        
        # Validate crime type
        try:
            crime_type = CrimeType(request.crime_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid crime type: {request.crime_type}")
        
        # Generate report
        report_response = await workflow.submit_answers_and_generate_report(
            description=request.user_input,
            crime_type_str=request.crime_type,
            answers=request.answers,
            case_id=request.case_id
        )
        
        # Update session
        if request.case_id in active_sessions:
            active_sessions[request.case_id]["step"] = "report_generated"
            active_sessions[request.case_id]["report_status"] = report_response.status
        
        print(f" Report generated successfully")
        print(f"   Status: {report_response.status}")
        if report_response.correlation_analysis:
            print(f"   Correlation: {report_response.correlation_analysis.status}")
        
        return report_response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f" Error in submit_report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================== SESSION MANAGEMENT =====================
@app.get("/api/v1/session/{case_id}")
def get_session_info(case_id: str):
    """Get current session information"""
    if case_id not in active_sessions:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    
    return {
        "case_id": case_id,
        "session": active_sessions[case_id]
    }

@app.get("/api/v1/sessions")
def list_sessions():
    """List all active sessions"""
    return {
        "total_active_sessions": len(active_sessions),
        "case_ids": list(active_sessions.keys())
    }

# ===================== LEGACY ENDPOINT =====================
@app.post("/generate-report")
async def generate_report_legacy(request: ReportRequest):
    """
    Legacy endpoint for backward compatibility
    Automatically classifies and generates report
    """
    try:
        # Start report
        start_result = await workflow.process_incident(request.user_input)
        case_id = start_result["case_id"]
        crime_type = start_result["recommendation"]
        
        # Generate questions
        questions = await workflow.generate_questions(
            request.user_input,
            CrimeType(crime_type)
        )
        
        return {
            "status": "needs_clarification",
            "case_id": case_id,
            "crime_type": crime_type,
            "confidence": start_result["confidence"],
            "questions": questions.questions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================== APPLICATION STARTUP =====================
if __name__ == "__main__":
    print("\n" + "="*70)
    print(">> ENHANCED CYBER CRIME REPORT SYSTEM".center(70))
    print("="*70)
    print("\nFeatures:")
    print("   [+] Crime Type Classification")
    print("   [+] Interactive Questioning")
    print("   [+] JSON Schema Reports")
    print("   [+] Correlation Detection")
    print("   [+] AI-Powered Analysis\n")
    print("[*] API Server: http://localhost:8000")
    print("[*] Documentation: http://localhost:8000/docs")
    print("[*] Admin: http://localhost:8000/redoc")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )