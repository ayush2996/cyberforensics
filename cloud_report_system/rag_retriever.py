# rag_retriever.py
"""
Stage Four: Retrieval-Augmented Prediction (RAG)
Uses past cases to validate and improve classification predictions.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from embeddings_manager import embeddings_manager
from correlation_engine import correlation_engine


@dataclass
class RetrievedCase:
    """Represents a retrieved historical case"""
    case_id: str
    crime_type: str
    similarity_score: float
    description: str
    resolution: Optional[str] = None
    confidence: Optional[float] = None


class RAGRetriever:
    """
    Retrieval-Augmented Generation for crime classification.
    Finds similar past cases and uses them to validate predictions.
    """
    
    def __init__(self, top_k: int = 5, similarity_threshold: float = 0.75):
        """
        Initialize RAG retriever.
        
        Args:
            top_k: Number of similar cases to retrieve
            similarity_threshold: Minimum cosine similarity (0-1)
        """
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.case_embeddings = {}  # Cache for case embeddings
    
    async def retrieve_similar_cases(
        self, 
        user_input: str, 
        crime_type: str = None,
        limit: int = None
    ) -> List[RetrievedCase]:
        """
        Retrieve similar cases from the database.
        
        Args:
            user_input: Current incident description
            crime_type: Optional filter by crime type
            limit: Override top_k for this query
            
        Returns:
            List of similar cases ranked by similarity
        """
        limit = limit or self.top_k
        
        # Get embedding for current input
        try:
            current_embedding = await embeddings_manager.get_embedding(user_input)
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []
        
        # Get cases from database
        cases = correlation_engine.case_database
        if not cases:
            return []
        
        # Filter by crime type if specified
        if crime_type:
            cases = [c for c in cases if c.get("crime_type") == crime_type]
        
        # Calculate similarity for each case
        similar_cases = []
        for case in cases:
            case_id = case.get("case_id", f"case_{datetime.now().timestamp()}")
            case_description = case.get("description", "")
            case_crime_type = case.get("crime_type", "unknown")
            
            # Get or compute embedding
            if case_id not in self.case_embeddings:
                try:
                    case_emb = await embeddings_manager.get_embedding(case_description)
                    self.case_embeddings[case_id] = case_emb
                except Exception as e:
                    print(f"Error embedding case {case_id}: {e}")
                    continue
            else:
                case_emb = self.case_embeddings[case_id]
            
            # Compute cosine similarity
            similarity = self._cosine_similarity(current_embedding, case_emb)
            
            # Only include if above threshold
            if similarity >= self.similarity_threshold:
                similar_cases.append(
                    RetrievedCase(
                        case_id=case_id,
                        crime_type=case_crime_type,
                        similarity_score=similarity,
                        description=case_description,
                        resolution=case.get("resolution"),
                        confidence=case.get("confidence")
                    )
                )
        
        # Sort by similarity and return top-k
        similar_cases.sort(key=lambda x: x.similarity_score, reverse=True)
        return similar_cases[:limit]
    
    async def predict_with_rag(
        self, 
        user_input: str, 
        predicted_crime_type: str,
        confidence: float
    ) -> Dict:
        """
        Use RAG to validate and improve prediction.
        
        Args:
            user_input: Current incident description
            predicted_crime_type: Crime type from earlier stages
            confidence: Confidence from earlier stages
            
        Returns:
            RAG-enhanced prediction with supporting cases
        """
        # Retrieve similar cases
        similar_cases = await self.retrieve_similar_cases(user_input, predicted_crime_type, limit=self.top_k)
        
        if not similar_cases:
            # No similar cases found
            return {
                "original_prediction": predicted_crime_type,
                "original_confidence": float(confidence),
                "rag_supported": False,
                "supporting_cases": [],
                "rag_confidence": float(confidence),
                "prediction_stability": "low"
            }
        
        # Analyze supporting cases
        case_types = {}
        total_similarity = 0
        
        for case in similar_cases:
            case_type = case.crime_type
            if case_type not in case_types:
                case_types[case_type] = {"count": 0, "total_similarity": 0}
            
            case_types[case_type]["count"] += 1
            case_types[case_type]["total_similarity"] += case.similarity_score
            total_similarity += case.similarity_score
        
        # Calculate consensus
        consensus_crime_type = max(case_types.items(), key=lambda x: x[1]["count"])[0]
        consensus_strength = case_types[consensus_crime_type]["count"] / len(similar_cases)
        
        # Determine if prediction is supported
        supported = consensus_crime_type == predicted_crime_type
        
        # Calculate enhanced confidence
        if supported:
            # Increase confidence if supported by cases
            rag_confidence = min(
                confidence + (0.15 * consensus_strength),
                0.99
            )
            stability = "high" if consensus_strength > 0.75 else "medium"
        else:
            # Reduce confidence if contradicted
            rag_confidence = max(
                confidence - (0.20 * (1 - consensus_strength)),
                0.3
            )
            stability = "low"
        
        return {
            "original_prediction": predicted_crime_type,
            "original_confidence": float(confidence),
            "rag_supported": bool(supported),
            "supporting_cases": [
                {
                    "case_id": case.case_id,
                    "crime_type": case.crime_type,
                    "similarity": round(float(case.similarity_score), 3),
                    "description_preview": case.description[:100] + "..." if len(case.description) > 100 else case.description
                }
                for case in similar_cases[:3]  # Top 3 cases
            ],
            "case_breakdown": {
                crime_type: {
                    "count": int(stats["count"]),
                    "avg_similarity": round(float(stats["total_similarity"] / stats["count"]), 3)
                }
                for crime_type, stats in case_types.items()
            },
            "consensus_crime_type": consensus_crime_type,
            "consensus_strength": round(float(consensus_strength), 3),
            "rag_confidence": round(float(rag_confidence), 3),
            "prediction_stability": stability,
            "recommendation": {
                "accept": bool(rag_confidence > 0.80),
                "reason": (
                    f"Prediction supported by {len(similar_cases)} similar cases with "
                    f"{round(consensus_strength * 100)}% consensus" if supported
                    else f"Prediction contradicted. {len(similar_cases)} similar cases suggest '{consensus_crime_type}'"
                )
            }
        }
    
    async def get_case_patterns(self, crime_type: str) -> Dict:
        """
        Get common patterns for a specific crime type from historical cases.
        
        Args:
            crime_type: Crime type to analyze
            
        Returns:
            Common patterns and characteristics
        """
        cases = [
            c for c in correlation_engine.case_database 
            if c.get("crime_type") == crime_type
        ]
        
        if not cases:
            return {"crime_type": crime_type, "patterns_found": 0}
        
        # Analyze patterns
        patterns = {
            "keywords": self._extract_common_keywords(cases),
            "avg_resolution_time": self._get_avg_resolution_time(cases),
            "common_indicators": self._extract_indicators(cases),
            "case_count": len(cases)
        }
        
        return {
            "crime_type": crime_type,
            "patterns_found": len(patterns["keywords"]),
            "patterns": patterns
        }
    
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
    
    @staticmethod
    def _extract_common_keywords(cases: List[Dict]) -> Dict:
        """Extract most common keywords from cases."""
        keyword_freq = {}
        
        for case in cases:
            description = case.get("description", "").lower().split()
            for word in description:
                # Filter short words
                if len(word) > 3:
                    keyword_freq[word] = keyword_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(
            keyword_freq.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return {word: count for word, count in sorted_keywords[:10]}
    
    @staticmethod
    def _get_avg_resolution_time(cases: List[Dict]) -> Optional[str]:
        """Calculate average resolution time for cases."""
        resolution_times = []
        
        for case in cases:
            created = case.get("created_at")
            resolved = case.get("resolved_at")
            
            if created and resolved:
                try:
                    start = datetime.fromisoformat(created)
                    end = datetime.fromisoformat(resolved)
                    delta = (end - start).days
                    resolution_times.append(delta)
                except:
                    pass
        
        if resolution_times:
            avg_days = sum(resolution_times) / len(resolution_times)
            return f"{int(avg_days)} days"
        
        return None
    
    @staticmethod
    def _extract_indicators(cases: List[Dict]) -> List[str]:
        """Extract common indicators from cases."""
        indicators = set()
        
        for case in cases:
            description = case.get("description", "").lower()
            
            # Common indicators
            if "phone" in description:
                indicators.add("phone_number")
            if "email" in description:
                indicators.add("email_address")
            if "money" in description or "dollar" in description:
                indicators.add("financial_loss")
            if "account" in description:
                indicators.add("account_access")
            if "password" in description or "credentials" in description:
                indicators.add("credentials")
            if "link" in description or "url" in description:
                indicators.add("malicious_link")
        
        return list(indicators)
    
    async def score_classification(
        self, 
        user_input: str,
        crime_type: str,
        confidence_from_stages: Dict
    ) -> Dict:
        """
        Final scoring combining all stage confidences with RAG validation.
        
        Args:
            user_input: Incident description
            crime_type: Predicted crime type
            confidence_from_stages: Dict with scores from each stage
            
        Returns:
            Final classification score
        """
        # Get RAG enhancement
        stage_avg = sum(confidence_from_stages.values()) / len(confidence_from_stages) if confidence_from_stages else 0.5
        rag_result = await self.predict_with_rag(user_input, crime_type, stage_avg)
        
        # Calculate final score
        final_score = {
            "crime_type": crime_type,
            "stage_confidences": confidence_from_stages,
            "stage_average": round(stage_avg, 3),
            "rag_enhancement": round(rag_result["rag_confidence"], 3),
            "final_confidence": round((stage_avg + rag_result["rag_confidence"]) / 2, 3),
            "supporting_cases": len(rag_result["supporting_cases"]),
            "prediction_stability": rag_result["prediction_stability"],
            "ready_for_submission": rag_result["recommendation"]["accept"],
            "reasoning": rag_result["recommendation"]["reason"]
        }
        
        return final_score


# Singleton instance
rag_retriever = RAGRetriever()
