# corrective_rag.py
"""
Corrective RAG: Learn from Human Corrections
Improves classification by learning from cases where humans correct the system.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from embeddings_manager import embeddings_manager


@dataclass
class CorrectionRecord:
    """Records a correction from human feedback"""
    case_id: str
    original_prediction: str
    corrected_prediction: str
    confidence_before: float
    incident_description: str
    correction_timestamp: str
    feedback_reason: Optional[str] = None
    correction_weight: float = 1.0  # Importance weight


class CorrectiveRAG:
    """
    Learns from human corrections to improve future predictions.
    
    Mechanism:
    1. Human corrects a misclassification
    2. System stores correction with embedding
    3. For future similar cases, system:
       - Finds corrections for similar incidents
       - Applies correction boosting to alternative types
       - Reduces confidence in originally predicted type
    """
    
    def __init__(self, min_correction_similarity: float = 0.80):
        """
        Initialize Corrective RAG.
        
        Args:
            min_correction_similarity: Min similarity to apply correction
        """
        self.corrections: List[CorrectionRecord] = []
        self.correction_embeddings: Dict[str, np.ndarray] = {}
        self.min_similarity = min_correction_similarity
        self.correction_pattern_memory = {}  # Track patterns that get corrected
    
    async def record_correction(
        self,
        case_id: str,
        original_prediction: str,
        corrected_prediction: str,
        confidence_before: float,
        incident_description: str,
        feedback_reason: Optional[str] = None
    ) -> Dict:
        """
        Record a human correction for learning.
        
        Args:
            case_id: ID of the case
            original_prediction: What system predicted
            corrected_prediction: What expert determined was correct
            confidence_before: System's confidence in wrong prediction
            incident_description: The incident text
            feedback_reason: Why the expert corrected (optional)
            
        Returns:
            Correction record and analysis
        """
        # Calculate correction impact
        impact = 1.0 - confidence_before  # Lower confidence = higher impact
        
        correction = CorrectionRecord(
            case_id=case_id,
            original_prediction=original_prediction,
            corrected_prediction=corrected_prediction,
            confidence_before=confidence_before,
            incident_description=incident_description,
            correction_timestamp=datetime.now().isoformat(),
            feedback_reason=feedback_reason,
            correction_weight=min(impact * 1.5, 2.0)  # Cap at 2x weight
        )
        
        # Get embedding for incident
        try:
            embedding = await embeddings_manager.get_embedding(incident_description)
            self.correction_embeddings[case_id] = embedding
        except Exception as e:
            print(f"Error embedding correction case {case_id}: {e}")
        
        # Store correction
        self.corrections.append(correction)
        
        # Update pattern memory
        pattern_key = f"{original_prediction}_to_{corrected_prediction}"
        if pattern_key not in self.correction_pattern_memory:
            self.correction_pattern_memory[pattern_key] = []
        self.correction_pattern_memory[pattern_key].append(case_id)
        
        return {
            "success": True,
            "case_id": case_id,
            "correction_recorded": True,
            "impact_score": correction.correction_weight,
            "total_corrections": len(self.corrections),
            "pattern_frequency": len(self.correction_pattern_memory.get(pattern_key, []))
        }
    
    async def apply_corrective_boosting(
        self,
        current_prediction: str,
        all_predictions: Dict[str, float],
        incident_description: str
    ) -> Dict:
        """
        Apply correction-based boosting to predictions.
        
        Args:
            current_prediction: Current top prediction
            all_predictions: Dict of {crime_type: confidence}
            incident_description: Incident text
            
        Returns:
            Adjusted predictions with correction boosting applied
        """
        if not self.corrections:
            return {
                "boosted_predictions": all_predictions,
                "corrections_applied": 0,
                "status": "no_corrections_available"
            }
        
        # Get incident embedding
        try:
            incident_embedding = await embeddings_manager.get_embedding(incident_description)
        except Exception as e:
            print(f"Error getting incident embedding: {e}")
            return {
                "boosted_predictions": all_predictions,
                "corrections_applied": 0,
                "error": str(e)
            }
        
        boosted_predictions = dict(all_predictions)
        corrections_applied = []
        
        # Find relevant corrections
        for correction in self.corrections:
            if correction.case_id not in self.correction_embeddings:
                continue
            
            # Calculate similarity
            corr_embedding = self.correction_embeddings[correction.case_id]
            similarity = self._cosine_similarity(incident_embedding, corr_embedding)
            
            # If similar incident was corrected, apply boosting
            if similarity >= self.min_similarity:
                wrong_type = correction.original_prediction
                correct_type = correction.corrected_prediction
                
                # Penalize wrong prediction
                if wrong_type in boosted_predictions:
                    penalty = similarity * correction.correction_weight * 0.2
                    boosted_predictions[wrong_type] = max(
                        boosted_predictions[wrong_type] - penalty,
                        0.1
                    )
                
                # Boost correct prediction
                if correct_type in boosted_predictions:
                    boost = similarity * correction.correction_weight * 0.15
                    boosted_predictions[correct_type] = min(
                        boosted_predictions[correct_type] + boost,
                        0.99
                    )
                
                corrections_applied.append({
                    "case_id": correction.case_id,
                    "similarity": similarity,
                    "wrong_type_penalized": wrong_type,
                    "correct_type_boosted": correct_type,
                    "weight": correction.correction_weight
                })
        
        # Renormalize predictions
        total = sum(boosted_predictions.values())
        if total > 0:
            boosted_predictions = {k: v / total for k, v in boosted_predictions.items()}
        
        return {
            "boosted_predictions": boosted_predictions,
            "corrections_applied": len(corrections_applied),
            "correction_details": corrections_applied,
            "status": "corrections_applied" if corrections_applied else "no_similar_corrections"
        }
    
    def get_common_error_patterns(self) -> Dict:
        """
        Identify common misclassification patterns.
        
        Returns:
            Analysis of common errors
        """
        error_patterns = {}
        
        for correction in self.corrections:
            pattern = f"{correction.original_prediction}  {correction.corrected_prediction}"
            
            if pattern not in error_patterns:
                error_patterns[pattern] = {
                    "count": 0,
                    "avg_confidence": 0,
                    "reasons": {}
                }
            
            error_patterns[pattern]["count"] += 1
            error_patterns[pattern]["avg_confidence"] += correction.confidence_before
            
            if correction.feedback_reason:
                error_patterns[pattern]["reasons"][correction.feedback_reason] = \
                    error_patterns[pattern]["reasons"].get(correction.feedback_reason, 0) + 1
        
        # Calculate averages
        for pattern, stats in error_patterns.items():
            if stats["count"] > 0:
                stats["avg_confidence"] = stats["avg_confidence"] / stats["count"]
        
        # Sort by frequency
        sorted_patterns = sorted(
            error_patterns.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        return {
            "total_corrections": len(self.corrections),
            "unique_patterns": len(error_patterns),
            "patterns": [
                {
                    "pattern": pattern,
                    "frequency": stats["count"],
                    "avg_wrong_confidence": round(stats["avg_confidence"], 3),
                    "common_reasons": stats["reasons"]
                }
                for pattern, stats in sorted_patterns
            ]
        }
    
    def get_learning_progress(self) -> Dict:
        """
        Get progress in learning from corrections.
        
        Returns:
            Learning metrics
        """
        if not self.corrections:
            return {"status": "no_corrections_recorded"}
        
        crime_type_corrections = {}
        
        for correction in self.corrections:
            wrong_type = correction.original_prediction
            
            if wrong_type not in crime_type_corrections:
                crime_type_corrections[wrong_type] = {
                    "misclassified_count": 0,
                    "avg_confidence_when_wrong": 0
                }
            
            crime_type_corrections[wrong_type]["misclassified_count"] += 1
            crime_type_corrections[wrong_type]["avg_confidence_when_wrong"] += correction.confidence_before
        
        # Calculate averages
        for crime_type, stats in crime_type_corrections.items():
            if stats["misclassified_count"] > 0:
                stats["avg_confidence_when_wrong"] = \
                    stats["avg_confidence_when_wrong"] / stats["misclassified_count"]
        
        return {
            "total_corrections_learned": len(self.corrections),
            "unique_patterns_learned": len(self.correction_pattern_memory),
            "crime_types_with_errors": crime_type_corrections,
            "highest_error_rate_type": max(
                crime_type_corrections.items(),
                key=lambda x: x[1]["misclassified_count"]
            )[0] if crime_type_corrections else None,
            "learning_strength": "STRONG" if len(self.corrections) > 20 else "MODERATE" if len(self.corrections) > 10 else "BUILDING"
        }
    
    def recommend_retraining(self) -> Optional[Dict]:
        """
        Recommend if system should be retrained based on corrections.
        
        Returns:
            Retraining recommendation or None
        """
        if len(self.corrections) < 5:
            return None  # Need more data
        
        # Analyze error patterns
        patterns = self.get_common_error_patterns()
        
        # Check if there's a dominant error pattern
        if patterns.get("patterns"):
            top_pattern = patterns["patterns"][0]
            if top_pattern["frequency"] >= 3:
                return {
                    "recommend_retraining": True,
                    "reason": f"Dominant error pattern: {top_pattern['pattern']} (occurred {top_pattern['frequency']} times)",
                    "priority": "HIGH" if top_pattern["frequency"] >= 5 else "MEDIUM",
                    "suggested_focus": f"Improve distinction between {top_pattern['pattern'].split('  ')}"
                }
        
        return None
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) == 0 or len(vec2) == 0:
            return 0.0
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Singleton instance
corrective_rag = CorrectiveRAG()

