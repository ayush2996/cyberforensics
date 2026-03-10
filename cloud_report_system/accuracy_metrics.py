# accuracy_metrics.py
"""
Accuracy & Confidence Metrics for the 4-Stage Crime Classification Pipeline.
Provides validation metrics used by crime_classifier_v3.py.
"""

from typing import Dict, List, Optional
import numpy as np


class AccuracyMetrics:
    """
    Calculates validation metrics for crime classification predictions.

    Metrics:
        1. top_k_confidence    — gap between top-1 and top-2 semantic scores
        2. entity_overlap      — keyword evidence found in user input
        3. expert_consistency  — agreement between prediction and RAG consensus
        4. prediction_stability — std deviation across stage confidence scores
    """

    # Thresholds for passing each metric
    THRESHOLDS = {
        "top_k_confidence":    0.05,   # top-1 must lead top-2 by at least 5%
        "entity_overlap":      0.10,   # at least 10% entity overlap
        "expert_consistency":  0.60,   # consensus similarity >= 60%
        "prediction_stability": 0.20,  # std dev across stages <= 0.20
    }

    # ── Individual metric calculators ─────────────────────────────────────────

    def calculate_top_k_confidence(
        self, top1_score: float, top2_score: float
    ) -> Dict:
        """
        Confidence gap between the top-1 and top-2 semantic router scores.
        A large gap means the top match is clearly dominant.
        """
        gap = float(top1_score) - float(top2_score)
        passes = gap >= self.THRESHOLDS["top_k_confidence"]
        return {
            "metric": "top_k_confidence",
            "top1_score": round(float(top1_score), 4),
            "top2_score": round(float(top2_score), 4),
            "gap": round(gap, 4),
            "threshold": self.THRESHOLDS["top_k_confidence"],
            "passes": passes,
            "score": round(min(gap / 0.3, 1.0), 4),   # normalise to 0–1
        }

    def calculate_entity_overlap(
        self, user_input: str, supporting_entities: List[str]
    ) -> Dict:
        """
        Fraction of supporting entities (keywords) found in the user input.
        """
        if not supporting_entities:
            return {
                "metric": "entity_overlap",
                "overlap_ratio": 0.0,
                "entities_found": [],
                "threshold": self.THRESHOLDS["entity_overlap"],
                "passes": False,
                "score": 0.0,
            }

        user_lower = user_input.lower()
        found = [e for e in supporting_entities if e.lower() in user_lower]
        ratio = len(found) / len(supporting_entities)
        passes = ratio >= self.THRESHOLDS["entity_overlap"]

        return {
            "metric": "entity_overlap",
            "overlap_ratio": round(ratio, 4),
            "entities_found": found,
            "entities_total": len(supporting_entities),
            "threshold": self.THRESHOLDS["entity_overlap"],
            "passes": passes,
            "score": round(ratio, 4),
        }

    def calculate_expert_consistency(
        self, prediction: str, consensus_type: str, similarity: float
    ) -> Dict:
        """
        Agreement between the pipeline prediction and the RAG consensus type.
        """
        type_match = prediction == consensus_type
        score = float(similarity) if type_match else float(similarity) * 0.5
        passes = score >= self.THRESHOLDS["expert_consistency"]

        return {
            "metric": "expert_consistency",
            "prediction": prediction,
            "consensus_type": consensus_type,
            "type_match": type_match,
            "similarity": round(float(similarity), 4),
            "score": round(score, 4),
            "threshold": self.THRESHOLDS["expert_consistency"],
            "passes": passes,
        }

    def calculate_prediction_stability(
        self, stage_scores: Dict[str, float]
    ) -> Dict:
        """
        Stability of confidence across the pipeline stages.
        Low std deviation = all stages agree = stable prediction.
        """
        if not stage_scores:
            return {
                "metric": "prediction_stability",
                "std_dev": 0.0,
                "mean": 0.0,
                "passes": False,
                "score": 0.0,
            }

        values = [float(v) for v in stage_scores.values()]
        std_dev = float(np.std(values))
        mean    = float(np.mean(values))
        passes  = std_dev <= self.THRESHOLDS["prediction_stability"]

        # Invert: low std = high stability score
        score = max(0.0, 1.0 - (std_dev / 0.5))

        return {
            "metric": "prediction_stability",
            "stage_scores": {k: round(float(v), 4) for k, v in stage_scores.items()},
            "std_dev": round(std_dev, 4),
            "mean": round(mean, 4),
            "threshold": self.THRESHOLDS["prediction_stability"],
            "passes": passes,
            "score": round(score, 4),
        }

    # ── Composite report ──────────────────────────────────────────────────────

    def generate_confidence_report(
        self,
        prediction: str,
        confidence: float,
        metrics_dict: Dict,
    ) -> Dict:
        """
        Combine individual metrics into a final confidence report.
        Determines whether the prediction is ready for submission.
        """
        passed = []
        failed = []

        for key, result in metrics_dict.items():
            if isinstance(result, dict) and "passes" in result:
                if result["passes"]:
                    passed.append(key)
                else:
                    failed.append(key)

        total   = len(passed) + len(failed)
        n_pass  = len(passed)
        metrics_passed_str = f"{n_pass}/{total}"

        # Weighted composite score
        metric_scores = []
        weights = {
            "top_k_confidence":     0.25,
            "entity_overlap":       0.20,
            "expert_consistency":   0.30,
            "prediction_stability": 0.25,
        }
        for key, weight in weights.items():
            m = metrics_dict.get(key, {})
            if isinstance(m, dict) and "score" in m:
                metric_scores.append(float(m["score"]) * weight)

        composite = sum(metric_scores) if metric_scores else float(confidence)
        composite = round(min(composite, 1.0), 4)

        ready = n_pass >= 3 and float(confidence) >= 0.65

        return {
            "prediction":          prediction,
            "raw_confidence":      round(float(confidence), 4),
            "composite_score":     composite,
            "metrics_passed":      metrics_passed_str,
            "passed_metrics":      passed,
            "failed_metrics":      failed,
            "ready_for_submission": ready,
            "submission_grade":    (
                "HIGH"   if composite >= 0.80 else
                "MEDIUM" if composite >= 0.60 else
                "LOW"
            ),
            **metrics_dict,
        }


# Singleton instance
accuracy_metrics = AccuracyMetrics()
