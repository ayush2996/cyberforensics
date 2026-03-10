# expert_analyzer.py
"""
Expert Analysis Flagging System
Identifies cases that need human review and marks new crime patterns.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class FlagReason(Enum):
    """Reasons for flagging cases for expert review"""
    LOW_CONFIDENCE = "low_confidence"
    NOVEL_PATTERN = "novel_pattern"
    CONFLICTING_SIGNALS = "conflicting_signals"
    NEW_CRIME_TYPE = "new_crime_type"
    RARE_COMBINATION = "rare_combination"
    METRIC_THRESHOLD_MISS = "metric_threshold_miss"
    AMBIGUOUS_INDICATORS = "ambiguous_indicators"
    CROSS_CATEGORY = "cross_category"


@dataclass
class ExpertFlag:
    """Flag created for expert analysis"""
    case_id: str
    reason: FlagReason
    confidence: float
    severity: str  # "HIGH", "MEDIUM", "LOW"
    supporting_evidence: List[str]
    predicted_crime_type: str
    alternative_types: List[str]
    timestamp: str
    reviewed: bool = False
    expert_determination: Optional[str] = None
    correction_feedback: Optional[str] = None


class ExpertAnalyzer:
    """
    Analyzes classifications to identify cases needing expert review.
    Automatically flags novel patterns and uncertain predictions.
    """
    
    def __init__(self, confidence_threshold: float = 0.70):
        """
        Initialize expert analyzer.
        
        Args:
            confidence_threshold: Confidence below this triggers review flag
        """
        self.confidence_threshold = confidence_threshold
        self.flagged_cases: List[ExpertFlag] = []
        self.novel_patterns = {}  # Track new/rare patterns
        self.crime_type_coverage = {
            "phishing": {"count": 0, "patterns": set()},
            "ransomware": {"count": 0, "patterns": set()},
            "identity_theft": {"count": 0, "patterns": set()},
            "fraud": {"count": 0, "patterns": set()},
            "malware": {"count": 0, "patterns": set()},
            "extortion": {"count": 0, "patterns": set()},
            "ddos": {"count": 0, "patterns": set()},
            "data_breach": {"count": 0, "patterns": set()},
            "hacking": {"count": 0, "patterns": set()},
            "spam": {"count": 0, "patterns": set()},
            "unknown": {"count": 0, "patterns": set()}
        }
    
    async def analyze_for_flagging(
        self,
        classification_result: Dict,
        incident_description: str,
        stage_outputs: Dict
    ) -> Optional[ExpertFlag]:
        """
        Determine if a case needs expert review.
        
        Args:
            classification_result: Full result from crime_classifier_v3
            incident_description: Original incident text
            stage_outputs: Outputs from all 4 stages
            
        Returns:
            ExpertFlag if flagging needed, None otherwise
        """
        case_id = f"case_{datetime.now().isoformat()}"
        predicted_type = classification_result.get("final_prediction", "unknown")
        confidence = classification_result.get("final_confidence", 0.0)
        metrics = classification_result.get("validation_metrics", {})
        stages = classification_result.get("stages", {})
        
        flags_triggered = []
        supporting_evidence = []
        alternative_types = []
        
        # Check 1: Low Confidence
        if confidence < self.confidence_threshold:
            flags_triggered.append(FlagReason.LOW_CONFIDENCE)
            supporting_evidence.append(f"Confidence {confidence:.2%} below threshold {self.confidence_threshold:.2%}")
        
        # Check 2: Metrics Failures
        metrics_passed = metrics.get("metrics_passed", "0/4")
        passed_count = int(metrics_passed.split("/")[0])
        if passed_count < 3:  # Less than 3 metrics pass
            flags_triggered.append(FlagReason.METRIC_THRESHOLD_MISS)
            supporting_evidence.append(f"Only {passed_count}/4 validation metrics passed")
        
        # Check 3: Prediction Stability Issues
        stability = metrics.get("prediction_stability", {})
        if stability.get("passes") is False:
            flags_triggered.append(FlagReason.CONFLICTING_SIGNALS)
            supporting_evidence.append("Stages show conflicting signals (high std_dev)")
            
            # Get alternatives from stages
            if "stage1_semantic_router" in stages:
                top_k = stages["stage1_semantic_router"].get("top_k_matches", [])
                for match in top_k[:2]:
                    if isinstance(match, dict):
                        alt_type = match.get("type")
                    else:
                        alt_type = match
                    if alt_type and alt_type != predicted_type:
                        alternative_types.append(str(alt_type))
        
        # Check 4: Novel/Rare Pattern
        pattern_strength = self._get_pattern_strength(stages)
        if pattern_strength < 0.5:
            flags_triggered.append(FlagReason.AMBIGUOUS_INDICATORS)
            supporting_evidence.append(f"Weak pattern signals (strength: {pattern_strength:.1%})")
        
        # Check 5: New Crime Type Coverage
        if predicted_type not in self.crime_type_coverage:
            flags_triggered.append(FlagReason.NEW_CRIME_TYPE)
            supporting_evidence.append(f"Crime type '{predicted_type}' not in standard 10 types")
        else:
            # Check for rare pattern within known type
            type_count = self.crime_type_coverage[predicted_type]["count"]
            if type_count < 3:
                flags_triggered.append(FlagReason.RARE_COMBINATION)
                supporting_evidence.append(f"Rare pattern for {predicted_type} (only {type_count} cases seen)")
        
        # Check 6: Cross-Category Signals
        rag_result = stages.get("stage4_rag_retriever", {})
        consensus_type = rag_result.get("consensus_crime_type")
        if consensus_type and consensus_type != predicted_type:
            flags_triggered.append(FlagReason.CROSS_CATEGORY)
            supporting_evidence.append(f"Predicted '{predicted_type}' but similar cases indicate '{consensus_type}'")
            if consensus_type not in alternative_types:
                alternative_types.append(consensus_type)
        
        # If any flags triggered, create ExpertFlag
        if flags_triggered:
            severity = self._determine_severity(flags_triggered, confidence)
            
            flag = ExpertFlag(
                case_id=case_id,
                reason=flags_triggered[0],  # Primary reason
                confidence=confidence,
                severity=severity,
                supporting_evidence=supporting_evidence,
                predicted_crime_type=predicted_type,
                alternative_types=list(set(alternative_types)),
                timestamp=datetime.now().isoformat()
            )
            
            self.flagged_cases.append(flag)
            return flag
        
        return None
    
    def process_expert_feedback(
        self,
        case_id: str,
        expert_determination: str,
        is_correction: bool = False
    ) -> Dict:
        """
        Process expert review feedback.
        
        Args:
            case_id: ID of flagged case
            expert_determination: Expert's determination of correct type
            is_correction: Whether this corrects a misclassification
            
        Returns:
            Feedback processing result
        """
        # Find the flag
        flag = None
        for f in self.flagged_cases:
            if f.case_id == case_id:
                flag = f
                break
        
        if not flag:
            return {"success": False, "error": "Flag not found"}
        
        # Update flag
        flag.reviewed = True
        flag.expert_determination = expert_determination
        flag.correction_feedback = "CORRECTION" if is_correction else "CONFIRMATION"
        
        # Update coverage tracking
        if expert_determination in self.crime_type_coverage:
            self.crime_type_coverage[expert_determination]["count"] += 1
        else:
            self.crime_type_coverage["unknown"]["count"] += 1
        
        return {
            "success": True,
            "case_id": case_id,
            "correction_applied": is_correction,
            "expert_determination": expert_determination,
            "feedback_type": "CORRECTION" if is_correction else "CONFIRMATION"
        }
    
    def get_flagged_cases(
        self, 
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 10
    ) -> List[ExpertFlag]:
        """
        Get flagged cases for expert review.
        
        Args:
            status: "reviewed" or "pending"
            severity: "HIGH", "MEDIUM", "LOW"
            limit: Max results
            
        Returns:
            List of flagged cases
        """
        results = self.flagged_cases
        
        if status == "pending":
            results = [f for f in results if not f.reviewed]
        elif status == "reviewed":
            results = [f for f in results if f.reviewed]
        
        if severity:
            results = [f for f in results if f.severity == severity]
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        return results[:limit]
    
    def get_case_coverage_report(self) -> Dict:
        """
        Get report on crime type coverage and patterns.
        
        Returns:
            Coverage analysis showing which types are well-covered vs rare
        """
        report = {
            "total_cases_seen": sum(c["count"] for c in self.crime_type_coverage.values()),
            "coverage_by_type": {},
            "coverage_gaps": [],
            "recommendations": []
        }
        
        for crime_type, stats in self.crime_type_coverage.items():
            count = stats["count"]
            pattern_count = len(stats["patterns"])
            
            report["coverage_by_type"][crime_type] = {
                "case_count": count,
                "pattern_variants": pattern_count,
                "coverage_level": "WELL_COVERED" if count >= 10 else "MODERATE" if count >= 5 else "SPARSE" if count > 0 else "NO_DATA"
            }
            
            # Identify gaps
            if count == 0:
                report["coverage_gaps"].append(crime_type)
            elif count < 5:
                report["recommendations"].append(f"Collect more {crime_type} examples (currently {count})")
        
        return report
    
    def get_pending_expert_reviews(self) -> Dict:
        """
        Get summary of cases awaiting expert review.
        
        Returns:
            Summary of flagged cases needing review
        """
        pending = [f for f in self.flagged_cases if not f.reviewed]
        
        if not pending:
            return {
                "pending_count": 0,
                "status": "CLEAR"
            }
        
        by_reason = {}
        by_severity = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for flag in pending:
            reason = flag.reason.value
            by_reason[reason] = by_reason.get(reason, 0) + 1
            by_severity[flag.severity] += 1
        
        return {
            "pending_count": len(pending),
            "by_severity": by_severity,
            "by_reason": by_reason,
            "highest_priority": pending[0] if pending else None
        }
    
    @staticmethod
    def _get_pattern_strength(stages: Dict) -> float:
        """Calculate overall pattern strength from stages"""
        if "stage3_pattern_matcher" in stages:
            return stages["stage3_pattern_matcher"].get("pattern_strength", 0.0)
        return 0.5  # Default if not available
    
    @staticmethod
    def _determine_severity(reasons: List[FlagReason], confidence: float) -> str:
        """
        Determine severity based on flag reasons and confidence.
        """
        critical_reasons = [
            FlagReason.NEW_CRIME_TYPE,
            FlagReason.CONFLICTING_SIGNALS
        ]
        
        if any(r in critical_reasons for r in reasons) or confidence < 0.50:
            return "HIGH"
        elif any(r == FlagReason.METRIC_THRESHOLD_MISS for r in reasons):
            return "MEDIUM"
        else:
            return "LOW"


# Singleton instance
expert_analyzer = ExpertAnalyzer()

