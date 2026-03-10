# crime_classifier_v3.py
"""
Multi-Stage Crime Classification System (v3)
Integrates all four stages for accurate crime prediction.
"""

from typing import Dict, Optional, Tuple, List
from enum import Enum
from llm_manager import llm
from semantic_router import semantic_router
from hierarchical_classifier import hierarchical_classifier
from pattern_matcher import pattern_matcher
from rag_retriever import rag_retriever
from accuracy_metrics import accuracy_metrics
from models import CrimeType



class CrimeClassifierV3:
    """
    Advanced multi-stage crime classification combining:
    1. Semantic routing (embedding-based)
    2. Hierarchical taxonomy
    3. Pattern matching
    4. RAG validation
    """
    
    def __init__(self):
        """Initialize the multi-stage classifier"""
        self.stages_enabled = {
            "semantic_router": True,
            "hierarchical_classifier": True,
            "pattern_matcher": True,
            "rag_retriever": True
        }
    
    async def classify_incident(
        self, 
        user_input: str,
        include_reasoning: bool = True
    ) -> Dict:
        """
        Classify crime incident through multi-stage pipeline.
        
        Args:
            user_input: Incident description
            include_reasoning: Include detailed reasoning path
            
        Returns:
            Classification result with confidence and supporting data
        """
        result = {
            "incident_description": user_input[:200] + "..." if len(user_input) > 200 else user_input,
            "stages": {},
            "final_prediction": None,
            "final_confidence": 0.0,
            "reasoning": [] if include_reasoning else None
        }
        
        # Stage 1: Semantic Router
        if self.stages_enabled["semantic_router"]:
            stage1_result = await self._stage1_semantic_routing(user_input)
            result["stages"]["stage1_semantic_router"] = stage1_result
            if include_reasoning:
                result["reasoning"].append(f"Stage 1: Semantic router predicts '{stage1_result['primary_match']}' with {stage1_result['primary_score']:.2%} confidence")
        
        # Stage 2: Hierarchical Classifier
        if self.stages_enabled["hierarchical_classifier"]:
            stage2_result = await self._stage2_hierarchical_classification(user_input)
            result["stages"]["stage2_hierarchical_classifier"] = stage2_result
            if include_reasoning:
                result["reasoning"].append(f"Stage 2: Hierarchical traversal predicts '{stage2_result['crime_type']}' through {stage2_result['depth']} levels")
        
        # Stage 3: Pattern Matching
        if self.stages_enabled["pattern_matcher"]:
            stage3_result = await self._stage3_pattern_matching(user_input)
            result["stages"]["stage3_pattern_matcher"] = stage3_result
            if include_reasoning:
                result["reasoning"].append(f"Stage 3: Found {stage3_result['signals_detected']} signal patterns (strength: {stage3_result['pattern_strength']:.2%})")
        
        # Aggregate scores
        aggregate_prediction, aggregate_confidence, stage_scores = self._aggregate_stages(result["stages"])
        result["aggregate_prediction"] = aggregate_prediction
        result["aggregate_confidence"] = aggregate_confidence
        result["stage_scores"] = stage_scores
        
        # Stage 4: RAG Validation
        if self.stages_enabled["rag_retriever"]:
            stage4_result = await self._stage4_rag_validation(
                user_input, 
                aggregate_prediction, 
                aggregate_confidence,
                stage_scores
            )
            result["stages"]["stage4_rag_retriever"] = stage4_result
            if include_reasoning:
                result["reasoning"].append(f"Stage 4: RAG validation finds {len(stage4_result['supporting_cases'])} similar cases, prediction {'SUPPORTED' if stage4_result['rag_supported'] else 'CONTRADICTED'}")
        
        # Calculate metrics
        entity_list = self._extract_supporting_entities(user_input, aggregate_prediction)
        metrics = self._calculate_validation_metrics(
            result["stages"],
            aggregate_prediction,
            aggregate_confidence,
            stage_scores,
            entity_list
        )
        result["validation_metrics"] = metrics
        
        # Final prediction
        if metrics['ready_for_submission']:
            result["final_prediction"] = aggregate_prediction
            result["final_confidence"] = aggregate_confidence
            result["submission_status"] = "APPROVED"
        else:
            result["final_prediction"] = aggregate_prediction
            result["final_confidence"] = aggregate_confidence
            result["submission_status"] = "NEEDS_REVIEW"
        
        return result
    
    async def _stage1_semantic_routing(self, user_input: str) -> Dict:
        """Execute Stage 1: Semantic Router"""
        # Route using semantic similarity
        routing_result = await semantic_router.multi_stage_route(user_input)
        
        return {
            "stage_name": "Semantic Router",
            "primary_match": routing_result.get("primary_match", "unknown"),
            "primary_score": routing_result.get("primary_score", 0.0),
            "top_k_matches": routing_result.get("top_k_matches", []),
            "confidence_gap": routing_result.get("confidence_gap", 0.0),
            "all_scores": routing_result.get("all_similarities", {})
        }
    
    async def _stage2_hierarchical_classification(self, user_input: str) -> Dict:
        """Execute Stage 2: Hierarchical Classifier"""
        hierarchy_result = await hierarchical_classifier.classify_hierarchical(user_input)
        
        return {
            "stage_name": "Hierarchical Taxonomy",
            "crime_type": hierarchy_result.get("crime_type", "unknown"),
            "classification_path": hierarchy_result.get("classification_path", []),
            "depth": len(hierarchy_result.get("classification_path", [])),
            "final_node": hierarchy_result.get("final_node", "unknown"),
            "path_visualization": hierarchical_classifier.visualize_path(hierarchy_result)
        }
    
    async def _stage3_pattern_matching(self, user_input: str) -> Dict:
        """Execute Stage 3: Pattern Matching"""
        signals = await pattern_matcher.analyze_signals(user_input)
        
        # Get strongest crime type match
        strongest_type = None
        strongest_weight = 0
        strongest_signals = {}
        
        if "all_signals" in signals:
            for crime_type, signal_data in signals["all_signals"].items():
                weight = signal_data.get("total_weight", 0)
                if weight > strongest_weight:
                    strongest_weight = weight
                    strongest_type = crime_type
                    strongest_signals = signal_data
        
        return {
            "stage_name": "Pattern Matcher",
            "strongest_match": strongest_type,
            "signals_detected": len(strongest_signals.get("signals_found", {})),
            "pattern_strength": strongest_signals.get("signal_count", 0) / 4,  # Normalized
            "signal_details": strongest_signals,
            "all_crime_type_signals": signals.get("all_signals", {})
        }
    
    async def _stage4_rag_validation(
        self,
        user_input: str,
        predicted_type: str,
        confidence: float,
        stage_scores: Dict
    ) -> Dict:
        """Execute Stage 4: RAG Retrieval"""
        rag_result = await rag_retriever.predict_with_rag(
            user_input,
            predicted_type,
            confidence
        )
        
        return {
            "stage_name": "RAG Retriever",
            "rag_supported": rag_result.get("rag_supported", False),
            "supporting_cases": rag_result.get("supporting_cases", []),
            "case_breakdown": rag_result.get("case_breakdown", {}),
            "consensus_crime_type": rag_result.get("consensus_crime_type", predicted_type),
            "consensus_strength": rag_result.get("consensus_strength", 0),
            "rag_confidence": rag_result.get("rag_confidence", confidence),
            "prediction_stability": rag_result.get("prediction_stability", "low"),
            "recommendation": rag_result.get("recommendation", {})
        }
    
    def _aggregate_stages(self, stages: Dict) -> Tuple[str, float, Dict]:
        """
        Aggregate scores from all stages.
        
        Returns:
            (predicted_crime_type, confidence, stage_scores_dict)
        """
        crime_votes = {}
        confidence_scores = {}
        
        # Collect votes from each stage
        if "stage1_semantic_router" in stages:
            s1 = stages["stage1_semantic_router"]
            crime_type = s1.get("primary_match")
            confidence = s1.get("primary_score", 0.0)
            confidence_scores["semantic_router"] = confidence
            crime_votes[crime_type] = crime_votes.get(crime_type, 0) + confidence * 0.25
        
        if "stage2_hierarchical_classifier" in stages:
            s2 = stages["stage2_hierarchical_classifier"]
            crime_type = s2.get("crime_type")
            # Base confidence on hierarchy depth (deeper = more certain)
            confidence = 0.5 + (min(s2.get("depth", 0), 3) / 3) * 0.3
            confidence_scores["hierarchical_classifier"] = confidence
            crime_votes[crime_type] = crime_votes.get(crime_type, 0) + confidence * 0.25
        
        if "stage3_pattern_matcher" in stages:
            s3 = stages["stage3_pattern_matcher"]
            crime_type = s3.get("strongest_match")
            confidence = min(s3.get("pattern_strength", 0) * 1.5, 1.0)  # Normalize
            confidence_scores["pattern_matcher"] = confidence
            if crime_type:
                crime_votes[crime_type] = crime_votes.get(crime_type, 0) + confidence * 0.25
        
        if "stage4_rag_retriever" in stages:
            s4 = stages["stage4_rag_retriever"]
            confidence = s4.get("rag_confidence", 0.5)
            confidence_scores["rag_retriever"] = confidence
            # RAG doesn't vote but influences final scoring
        
        # Weighted average of confidence scores
        if confidence_scores:
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
        else:
            avg_confidence = 0.5
        
        # Pick the crime type with most votes
        if crime_votes:
            predicted_crime_type = max(crime_votes.items(), key=lambda x: x[1])[0]
        else:
            predicted_crime_type = "fraud"  # Default fallback
        
        return predicted_crime_type, avg_confidence, confidence_scores
    
    def _calculate_validation_metrics(
        self,
        stages: Dict,
        prediction: str,
        confidence: float,
        stage_scores: Dict,
        supporting_entities: List[str]
    ) -> Dict:
        """Calculate comprehensive validation metrics"""
        metrics_dict = {}
        
        # Top-K Confidence
        if "stage1_semantic_router" in stages and "stage2_hierarchical_classifier" in stages:
            s1_score = float(stages["stage1_semantic_router"].get("primary_similarity", 0.0))
            top_k_results = stages["stage1_semantic_router"].get("top_k_matches", [])
            
            second_score = 0.0
            if len(top_k_results) > 1:
                second = top_k_results[1]
                if isinstance(second, tuple):
                    second_score = float(second[1])  # Extract score from tuple
                elif isinstance(second, dict):
                    second_score = float(second.get("score", 0.0))
                else:
                    second_score = float(second)
            
            metrics_dict["top_k_confidence"] = accuracy_metrics.calculate_top_k_confidence(
                s1_score, second_score
            )
        
        # Entity Overlap
        user_input_preview = stages.get("description", "")[:200]  # Dummy for demo
        metrics_dict["entity_overlap"] = accuracy_metrics.calculate_entity_overlap(
            user_input_preview,
            supporting_entities
        )
        
        # Expert Consistency
        if "stage4_rag_retriever" in stages:
            s4 = stages["stage4_rag_retriever"]
            consensus = s4.get("consensus_crime_type", prediction)
            similarity = s4.get("consensus_strength", 0.75)
            
            metrics_dict["expert_consistency"] = accuracy_metrics.calculate_expert_consistency(
                prediction, consensus, similarity
            )
        else:
            metrics_dict["expert_consistency"] = {
                "metric": "expert_consistency",
                "status": "no_rag_data"
            }
        
        # Prediction Stability
        metrics_dict["prediction_stability"] = accuracy_metrics.calculate_prediction_stability(
            stage_scores
        )
        
        # Generate comprehensive report
        confidence_report = accuracy_metrics.generate_confidence_report(
            prediction, confidence, metrics_dict
        )
        
        return confidence_report
    
    def _extract_supporting_entities(self, user_input: str, crime_type: str) -> List[str]:
        """Extract entities that support the classification"""
        entities = []
        user_input_lower = user_input.lower()
        
        # Get patterns for this crime type
        if crime_type in pattern_matcher.signal_patterns:
            patterns = pattern_matcher.signal_patterns[crime_type]
            for pattern in patterns:
                for keyword in pattern.keywords:
                    if keyword in user_input_lower:
                        entities.append(keyword)
        
        return list(set(entities))[:5]  # Return unique top 5


# Singleton instance
crime_classifier_v3 = CrimeClassifierV3()

