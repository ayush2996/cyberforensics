# accuracy_metrics.py
"""
Accuracy Metrics & Confidence Scoring Framework
Tracks and validates classification accuracy across all stages.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ClassificationMetric:
    """Individual classification evaluation"""
    incident_id: str
    predicted_crime_type: str
    actual_crime_type: Optional[str]
    confidence: float
    stage_scores: Dict
    supporting_entities: List[str]
    timestamp: str
    correct: Optional[bool] = None


class AccuracyMetrics:
    """
    Comprehensive accuracy tracking and validation framework.
    
    Metrics tracked:
    - Top-K Confidence: Gap between 1st and 2nd choice (threshold >0.80)
    - Entity Overlap: Relevant indicators present (threshold >60%)
    - Expert Consistency: Match with verified cases (threshold >0.85)
    - Prediction Stability: Multi-stage agreement (threshold >0.75)
    """
    
    def __init__(self):
        """Initialize metrics tracker"""
        self.metrics_history: List[ClassificationMetric] = []
        self.stage_performance = {
            "semantic_router": {"total": 0, "accurate": 0},
            "hierarchical_classifier": {"total": 0, "accurate": 0},
            "pattern_matcher": {"total": 0, "accurate": 0},
            "rag_retriever": {"total": 0, "accurate": 0},
        }
        self.crime_type_accuracy = {}
    
    def evaluate_classification(
        self,
        incident_id: str,
        predicted_crime_type: str,
        actual_crime_type: Optional[str],
        confidence: float,
        stage_scores: Dict,
        supporting_entities: List[str] = None
    ) -> ClassificationMetric:
        """
        Log and evaluate a single classification.
        
        Args:
            incident_id: Unique identifier for this incident
            predicted_crime_type: What the system predicted
            actual_crime_type: Ground truth (if available)
            confidence: Final confidence score (0-1)
            stage_scores: Dict with scores from each stage
            supporting_entities: Keywords or indicators found
            
        Returns:
            ClassificationMetric with evaluation results
        """
        supporting_entities = supporting_entities or []
        
        metric = ClassificationMetric(
            incident_id=incident_id,
            predicted_crime_type=predicted_crime_type,
            actual_crime_type=actual_crime_type,
            confidence=confidence,
            stage_scores=stage_scores,
            supporting_entities=supporting_entities,
            timestamp=datetime.now().isoformat(),
            correct=(predicted_crime_type == actual_crime_type) if actual_crime_type else None
        )
        
        self.metrics_history.append(metric)
        
        # Update stage performance if ground truth available
        if actual_crime_type:
            for stage_name, score in stage_scores.items():
                if stage_name in self.stage_performance:
                    self.stage_performance[stage_name]["total"] += 1
                    # Consider stage "accurate" if confident (>0.7)
                    if score > 0.70:
                        self.stage_performance[stage_name]["accurate"] += 1
            
            # Update crime type accuracy
            if predicted_crime_type not in self.crime_type_accuracy:
                self.crime_type_accuracy[predicted_crime_type] = {"total": 0, "correct": 0}
            
            self.crime_type_accuracy[predicted_crime_type]["total"] += 1
            if metric.correct:
                self.crime_type_accuracy[predicted_crime_type]["correct"] += 1
        
        return metric
    
    def calculate_top_k_confidence(
        self, 
        first_score: float, 
        second_score: float
    ) -> Dict:
        """
        Calculate confidence gap between top 2 predictions.
        Threshold: >0.80 for high confidence.
        
        Args:
            first_score: Top prediction confidence
            second_score: Second best prediction confidence
            
        Returns:
            Confidence gap analysis
        """
        gap = first_score - second_score
        
        return {
            "metric": "top_k_confidence",
            "first_score": round(first_score, 3),
            "second_score": round(second_score, 3),
            "confidence_gap": round(gap, 3),
            "threshold": 0.80,
            "passes": gap > 0.80,
            "interpretation": (
                "High confidence - clear winner" if gap > 0.80
                else "Medium confidence - some uncertainty" if gap > 0.50
                else "Low confidence - predictions are close"
            )
        }
    
    def calculate_entity_overlap(
        self, 
        user_input: str, 
        supporting_entities: List[str]
    ) -> Dict:
        """
        Calculate how many relevant indicators are present.
        Threshold: >60% overlap.
        
        Args:
            user_input: Original incident description
            supporting_entities: Keywords/indicators found
            
        Returns:
            Entity overlap analysis
        """
        if not supporting_entities:
            overlap = 0.0
        else:
            matches = sum(1 for entity in supporting_entities if entity.lower() in user_input.lower())
            overlap = matches / len(supporting_entities) if supporting_entities else 0.0
        
        return {
            "metric": "entity_overlap",
            "supporting_entities": len(supporting_entities),
            "entities_found_in_input": sum(1 for e in supporting_entities if e.lower() in user_input.lower()),
            "overlap_percentage": round(overlap * 100, 1),
            "threshold": 60.0,
            "passes": overlap > 0.60,
            "interpretation": (
                "Strong evidence - most indicators present" if overlap > 0.75
                else "Moderate evidence - some indicators present" if overlap > 0.60
                else "Weak evidence - few indicators present"
            )
        }
    
    def calculate_expert_consistency(
        self, 
        current_prediction: str, 
        similar_case_consensus: str,
        vector_similarity: float
    ) -> Dict:
        """
        Check if prediction matches historical cases.
        Threshold: >0.85 vector similarity OR exact type match.
        
        Args:
            current_prediction: Current prediction
            similar_case_consensus: What similar cases predict
            vector_similarity: Vector similarity to cases (0-1)
            
        Returns:
            Expert consistency analysis
        """
        type_match = current_prediction == similar_case_consensus
        vector_passes = vector_similarity > 0.85
        passes = type_match or vector_passes
        
        return {
            "metric": "expert_consistency",
            "current_prediction": current_prediction,
            "similar_cases_consensus": similar_case_consensus,
            "type_match": type_match,
            "vector_similarity": round(vector_similarity, 3),
            "vector_threshold": 0.85,
            "vector_passes": vector_passes,
            "threshold": "type_match OR (vector_similarity > 0.85)",
            "passes": passes,
            "interpretation": (
                "Highly consistent with historical cases" if vector_similarity > 0.85 and type_match
                else "Consistent with historical cases" if passes
                else "Diverges from historical patterns"
            )
        }
    
    def calculate_prediction_stability(
        self, 
        stage_scores: Dict
    ) -> Dict:
        """
        Check if multiple stages agree.
        Threshold: Standard deviation <0.15.
        
        Args:
            stage_scores: Dict with scores from each stage
            
        Returns:
            Prediction stability analysis
        """
        if not stage_scores or len(stage_scores) < 2:
            return {
                "metric": "prediction_stability",
                "stage_count": len(stage_scores),
                "stability": "insufficient_stages",
                "passes": False
            }
        
        scores = list(stage_scores.values())
        mean_score = sum(scores) / len(scores)
        variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
        std_dev = variance ** 0.5
        
        return {
            "metric": "prediction_stability",
            "stages": len(stage_scores),
            "mean_score": round(mean_score, 3),
            "std_dev": round(std_dev, 3),
            "threshold": 0.15,
            "passes": std_dev < 0.15,
            "stage_variance": {stage: round(score - mean_score, 3) for stage, score in stage_scores.items()},
            "interpretation": (
                "High stability - all stages agree" if std_dev < 0.10
                else "Good stability - stages mostly agree" if std_dev < 0.15
                else "Low stability - stages diverge"
            )
        }
    
    def generate_confidence_report(
        self,
        prediction: str,
        confidence: float,
        metrics_dict: Dict
    ) -> Dict:
        """
        Generate comprehensive confidence report.
        
        Args:
            prediction: Final crime type prediction
            confidence: Final confidence score (0-1)
            metrics_dict: Dict with all metric evaluations
            
        Returns:
            Comprehensive confidence report
        """
        # Calculate passing metrics
        passing_metrics = sum(1 for m in metrics_dict.values() if m.get("passes", False))
        total_metrics = len(metrics_dict)
        
        # Determine overall confidence level
        if confidence > 0.85 and passing_metrics == total_metrics:
            confidence_level = "VERY_HIGH"
            ready_for_submission = True
        elif confidence > 0.75 and passing_metrics >= total_metrics - 1:
            confidence_level = "HIGH"
            ready_for_submission = True
        elif confidence > 0.65 and passing_metrics >= total_metrics - 1:
            confidence_level = "MODERATE"
            ready_for_submission = False
        else:
            confidence_level = "LOW"
            ready_for_submission = False
        
        return {
            "prediction": prediction,
            "confidence_score": round(confidence, 3),
            "confidence_level": confidence_level,
            "metrics": metrics_dict,
            "metrics_passed": f"{passing_metrics}/{total_metrics}",
            "ready_for_submission": ready_for_submission,
            "recommendation": {
                "action": "SUBMIT" if ready_for_submission else "REVIEW",
                "reason": (
                    f"Prediction has {confidence_level} confidence with {passing_metrics}/{total_metrics} validation metrics passed"
                )
            }
        }
    
    def get_stage_performance(self) -> Dict:
        """Get performance metrics for each classification stage."""
        performance = {}
        
        for stage, stats in self.stage_performance.items():
            total = stats["total"]
            accurate = stats["accurate"]
            
            if total > 0:
                accuracy = (accurate / total) * 100
                performance[stage] = {
                    "total_predictions": total,
                    "accurate": accurate,
                    "accuracy_percentage": round(accuracy, 1),
                    "confidence_trend": "improving" if accuracy > 75 else "needs_work"
                }
            else:
                performance[stage] = {
                    "total_predictions": 0,
                    "status": "no_data"
                }
        
        return performance
    
    def get_crime_type_accuracy(self, crime_type: Optional[str] = None) -> Dict:
        """
        Get accuracy for specific crime type or all types.
        
        Args:
            crime_type: Optional specific type to query
            
        Returns:
            Accuracy breakdown by crime type
        """
        if crime_type:
            if crime_type in self.crime_type_accuracy:
                stats = self.crime_type_accuracy[crime_type]
                total = stats["total"]
                if total > 0:
                    accuracy = (stats["correct"] / total) * 100
                    return {
                        "crime_type": crime_type,
                        "total_cases": total,
                        "correct": stats["correct"],
                        "accuracy_percentage": round(accuracy, 1)
                    }
            return {"crime_type": crime_type, "status": "no_data"}
        
        # All types
        accuracy_breakdown = {}
        for crime_type, stats in self.crime_type_accuracy.items():
            total = stats["total"]
            if total > 0:
                accuracy = (stats["correct"] / total) * 100
                accuracy_breakdown[crime_type] = {
                    "total_cases": total,
                    "correct": stats["correct"],
                    "accuracy_percentage": round(accuracy, 1)
                }
        
        return accuracy_breakdown
    
    def get_summary_metrics(self) -> Dict:
        """Get overall system performance summary."""
        if not self.metrics_history:
            return {"status": "no_classifications_yet"}
        
        total = len(self.metrics_history)
        correct = sum(1 for m in self.metrics_history if m.correct)
        avg_confidence = sum(m.confidence for m in self.metrics_history) / total if total > 0 else 0
        
        return {
            "total_classifications": total,
            "correct_classifications": correct,
            "overall_accuracy": round((correct / total * 100) if total > 0 else 0, 1),
            "average_confidence": round(avg_confidence, 3),
            "stage_performance": self.get_stage_performance(),
            "crime_type_accuracy": self.get_crime_type_accuracy(),
            "system_ready": (correct / total > 0.80) if total > 0 else False
        }


# Singleton instance
accuracy_metrics = AccuracyMetrics()

