# self_rag.py
"""
Self-RAG: Self-Retrieval & Augmented Generation
System validates its own predictions and can revise them.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np
from correlation_engine import correlation_engine
from embeddings_manager import embeddings_manager


@dataclass
class ValidationCheckpoint:
    """Represents a self-validation checkpoint"""
    check_name: str
    passed: bool
    confidence_delta: float  # How much to adjust confidence
    reasoning: str


class SelfRAG:
    """
    Self-Retrieval-Augmented Generation.
    
    Process:
    1. Get initial prediction
    2. System validates itself using:
       - Consistency checking (do multiple approaches agree?)
       - Knowledge grounding (is prediction supported by cases?)
       - Confidence calibration (is confidence justified?)
    3. If validation fails, system can:
       - Revise prediction
       - Request human review
       - Explain uncertainty
    """
    
    def __init__(self, revision_enabled: bool = True):
        """
        Initialize Self-RAG.
        
        Args:
            revision_enabled: Allow system to revise its own predictions
        """
        self.revision_enabled = revision_enabled
        self.validation_history = []
    
    async def validate_prediction(
        self,
        prediction: str,
        confidence: float,
        stage_outputs: Dict,
        incident_description: str
    ) -> Dict:
        """
        Perform comprehensive self-validation.
        
        Args:
            prediction: Current prediction
            confidence: Current confidence
            stage_outputs: Outputs from all 4 stages
            incident_description: Original incident
            
        Returns:
            Validation result with potential revisions
        """
        checkpoints = []
        total_confidence_delta = 0
        
        # Checkpoint 1: Internal Consistency
        cp1 = await self._check_internal_consistency(stage_outputs, prediction)
        checkpoints.append(cp1)
        total_confidence_delta += cp1.confidence_delta
        
        # Checkpoint 2: Knowledge Grounding
        cp2 = await self._check_knowledge_grounding(prediction, incident_description)
        checkpoints.append(cp2)
        total_confidence_delta += cp2.confidence_delta
        
        # Checkpoint 3: Confidence Calibration
        cp3 = await self._check_confidence_calibration(confidence, stage_outputs)
        checkpoints.append(cp3)
        total_confidence_delta += cp3.confidence_delta
        
        # Checkpoint 4: Edge Case Detection
        cp4 = await self._check_edge_cases(incident_description, prediction)
        checkpoints.append(cp4)
        total_confidence_delta += cp4.confidence_delta
        
        # Checkpoint 5: Cross-Domain Validation
        cp5 = await self._check_cross_domain(prediction, stage_outputs)
        checkpoints.append(cp5)
        total_confidence_delta += cp5.confidence_delta
        
        # Calculate adjusted confidence
        adjusted_confidence = max(0.1, min(0.99, confidence + total_confidence_delta))
        
        # Check if revision is needed
        needs_revision = any(not cp.passed for cp in checkpoints)
        revision_suggestion = None
        
        if needs_revision and self.revision_enabled:
            revision_suggestion = await self._suggest_revision(
                prediction,
                stage_outputs,
                checkpoints
            )
        
        result = {
            "original_prediction": prediction,
            "original_confidence": confidence,
            "validation_checkpoints": [
                {
                    "name": cp.check_name,
                    "passed": cp.passed,
                    "confidence_delta": round(cp.confidence_delta, 3),
                    "reasoning": cp.reasoning
                }
                for cp in checkpoints
            ],
            "checkpoints_passed": sum(1 for cp in checkpoints if cp.passed),
            "total_checkpoints": len(checkpoints),
            "confidence_adjustment": round(total_confidence_delta, 3),
            "adjusted_confidence": round(adjusted_confidence, 3),
            "needs_revision": needs_revision,
            "revision_suggestion": revision_suggestion,
            "recommendation": self._generate_recommendation(
                needs_revision,
                adjusted_confidence,
                sum(1 for cp in checkpoints if cp.passed)
            )
        }
        
        self.validation_history.append(result)
        return result
    
    async def _check_internal_consistency(
        self,
        stage_outputs: Dict,
        prediction: str
    ) -> ValidationCheckpoint:
        """
        Check if all stages agree on prediction direction.
        """
        agreements = 0
        stage_predictions = []
        
        if "stage1_semantic_router" in stage_outputs:
            s1_pred = stage_outputs["stage1_semantic_router"].get("primary_match")
            stage_predictions.append(s1_pred)
            if s1_pred == prediction:
                agreements += 1
        
        if "stage2_hierarchical_classifier" in stage_outputs:
            s2_pred = stage_outputs["stage2_hierarchical_classifier"].get("crime_type")
            stage_predictions.append(s2_pred)
            if s2_pred == prediction:
                agreements += 1
        
        if "stage3_pattern_matcher" in stage_outputs:
            s3_pred = stage_outputs["stage3_pattern_matcher"].get("strongest_match")
            if s3_pred:
                stage_predictions.append(s3_pred)
                if s3_pred == prediction:
                    agreements += 1
        
        # Pass if majority agree
        passed = agreements >= 2 if len(stage_predictions) >= 2 else agreements >= 1
        
        confidence_delta = 0.1 if passed else -0.1
        reasoning = f"{agreements}/{len(stage_predictions)} stages agree on '{prediction}'"
        
        return ValidationCheckpoint(
            check_name="Internal Consistency",
            passed=passed,
            confidence_delta=confidence_delta,
            reasoning=reasoning
        )
    
    async def _check_knowledge_grounding(
        self,
        prediction: str,
        incident_description: str
    ) -> ValidationCheckpoint:
        """
        Check if prediction is grounded in known cases.
        """
        cases = correlation_engine.case_database
        matching_cases = [c for c in cases if c.get("crime_type") == prediction]
        
        # Pass if we have similar cases
        passed = len(matching_cases) > 0
        
        if passed:
            # Calculate how similar to existing cases
            confidence_delta = min(len(matching_cases) / 10, 0.15)  # Max +0.15
            reasoning = f"Grounded in {len(matching_cases)} known '{prediction}' cases"
        else:
            confidence_delta = -0.15
            reasoning = f"No known cases for prediction '{prediction}' (novel pattern)"
        
        return ValidationCheckpoint(
            check_name="Knowledge Grounding",
            passed=passed,
            confidence_delta=confidence_delta,
            reasoning=reasoning
        )
    
    async def _check_confidence_calibration(
        self,
        confidence: float,
        stage_outputs: Dict
    ) -> ValidationCheckpoint:
        """
        Check if confidence is justified by uncertainty in stages.
        """
        # Extract confidence from stages
        stage_confidences = []
        
        if "stage1_semantic_router" in stage_outputs:
            gap = stage_outputs["stage1_semantic_router"].get("confidence_gap", 0)
            stage_confidences.append(gap)
        
        if "stage2_hierarchical_classifier" in stage_outputs:
            depth = stage_outputs["stage2_hierarchical_classifier"].get("depth", 0)
            stage_confidences.append(0.5 + (depth / 3) * 0.4)  # 0.5-0.9
        
        if len(stage_confidences) < 2:
            return ValidationCheckpoint(
                check_name="Confidence Calibration",
                passed=True,
                confidence_delta=0,
                reasoning="Insufficient data for calibration check"
            )
        
        # Check if reported confidence aligns with stage data
        min_stage_conf = min(stage_confidences)
        max_stage_conf = max(stage_confidences)
        
        # Confidence should be in reasonable range
        passed = min_stage_conf <= confidence <= max(1.0, max_stage_conf)
        
        if passed:
            confidence_delta = 0.05
            reasoning = f"Confidence {confidence:.2%} is well-calibrated to stage data"
        else:
            confidence_delta = -0.1
            reasoning = f"Confidence {confidence:.2%} unjustified by stage uncertainty"
        
        return ValidationCheckpoint(
            check_name="Confidence Calibration",
            passed=passed,
            confidence_delta=confidence_delta,
            reasoning=reasoning
        )
    
    async def _check_edge_cases(
        self,
        incident_description: str,
        prediction: str
    ) -> ValidationCheckpoint:
        """
        Check for specific edge case patterns.
        """
        edge_case_indicators = {
            "phishing": ["verify", "confirm", "click", "credentials"],
            "ransomware": ["encrypted", "ransom", "bitcoin", "locked"],
            "fraud": ["money", "payment", "transferred", "lost"],
            "identity_theft": ["account", "opened", "credit"],
            "hacking": ["unauthorized", "access", "password", "compromised"]
        }
        
        description_lower = incident_description.lower()
        
        # Check if prediction has relevant edge case indicators
        if prediction in edge_case_indicators:
            indicators = edge_case_indicators[prediction]
            found = sum(1 for ind in indicators if ind in description_lower)
            
            passed = found >= 1  # At least one indicator
            confidence_delta = 0.05 if passed else -0.08
            reasoning = f"Found {found} edge case indicators for '{prediction}'"
        else:
            passed = True  # Unknown type, pass
            confidence_delta = 0
            reasoning = f"No specific edge cases checked for '{prediction}'"
        
        return ValidationCheckpoint(
            check_name="Edge Case Detection",
            passed=passed,
            confidence_delta=confidence_delta,
            reasoning=reasoning
        )
    
    async def _check_cross_domain(
        self,
        prediction: str,
        stage_outputs: Dict
    ) -> ValidationCheckpoint:
        """
        Check for cross-domain consistency (RAG consensus).
        """
        if "stage4_rag_retriever" not in stage_outputs:
            return ValidationCheckpoint(
                check_name="Cross-Domain Validation",
                passed=True,
                confidence_delta=0,
                reasoning="RAG stage not available"
            )
        
        rag = stage_outputs["stage4_rag_retriever"]
        consensus_type = rag.get("consensus_crime_type")
        supported = rag.get("rag_supported", False)
        
        passed = supported
        
        if passed:
            confidence_delta = 0.1
            reasoning = f"Cross-domain consensus confirms '{prediction}'"
        else:
            confidence_delta = -0.15
            reasoning = f"Cross-domain consensus contradicts '{prediction}' (suggests '{consensus_type}')"
        
        return ValidationCheckpoint(
            check_name="Cross-Domain Validation",
            passed=passed,
            confidence_delta=confidence_delta,
            reasoning=reasoning
        )
    
    async def _suggest_revision(
        self,
        current_prediction: str,
        stage_outputs: Dict,
        checkpoints: List[ValidationCheckpoint]
    ) -> Dict:
        """
        Suggest a revised prediction if validation failed.
        """
        # Get alternative predictions
        alternatives = {
            "from_stage1": stage_outputs.get("stage1_semantic_router", {}).get("top_k_matches", []),
            "from_stage2": stage_outputs.get("stage2_hierarchical_classifier", {}).get("final_node"),
            "from_rag": stage_outputs.get("stage4_rag_retriever", {}).get("consensus_crime_type")
        }
        
        failed_checks = [cp for cp in checkpoints if not cp.passed]
        primary_issue = failed_checks[0].check_name if failed_checks else "Unknown"
        
        return {
            "should_revise": True,
            "current_prediction": current_prediction,
            "alternative_predictions": alternatives,
            "primary_issue": primary_issue,
            "suggested_action": "HUMAN_REVIEW",
            "explanation": f"Prediction failed {len(failed_checks)}/{len(checkpoints)} validation checks"
        }
    
    def _generate_recommendation(
        self,
        needs_revision: bool,
        confidence: float,
        checks_passed: int
    ) -> str:
        """Generate recommendation based on validation."""
        if not needs_revision and confidence > 0.85 and checks_passed >= 4:
            return "SUBMIT - High confidence, validation successful"
        elif not needs_revision and confidence > 0.75 and checks_passed >= 3:
            return "SUBMIT - Good confidence, most checks passed"
        elif needs_revision and confidence > 0.70:
            return "REVIEW - Improvement suggested but acceptable"
        elif needs_revision and confidence > 0.60:
            return "HUMAN_REVIEW - Multiple validation failures"
        else:
            return "ESCALATE - Low confidence and validation failures"
    
    def get_validation_statistics(self) -> Dict:
        """
        Get statistics on self-validation performance.
        
        Returns:
            Summary of validation history
        """
        if not self.validation_history:
            return {"status": "no_validations_yet"}
        
        total_validations = len(self.validation_history)
        revisions_suggested = sum(1 for v in self.validation_history if v["needs_revision"])
        avg_confidence_original = sum(v["original_confidence"] for v in self.validation_history) / total_validations
        avg_confidence_adjusted = sum(v["adjusted_confidence"] for v in self.validation_history) / total_validations
        
        return {
            "total_validations": total_validations,
            "revisions_suggested": revisions_suggested,
            "revision_rate": round(revisions_suggested / total_validations * 100, 1),
            "avg_confidence_before": round(avg_confidence_original, 3),
            "avg_confidence_after": round(avg_confidence_adjusted, 3),
            "confidence_improvement": round(avg_confidence_adjusted - avg_confidence_original, 3),
            "avg_checks_passed": sum(v["checkpoints_passed"] for v in self.validation_history) / total_validations
        }


# Singleton instance
self_rag = SelfRAG()

