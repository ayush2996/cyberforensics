# LEARNING_SYSTEM_GUIDE.md

## Complete Learning System: Professional Development Framework

### System Overview

The cyber crime reporting system now includes four advanced learning mechanisms that continuously improve accuracy and adapt to new crime patterns:

```
Classification Pipeline
        ↓
   [4-Stage Classifier]
        ↓
    Prediction → Self-RAG Validation
                    ↓
              Checkpoints Passed? 
              /              \
            YES               NO
             ↓                 ↓
          Submit      Expert Flagging
                     (Human Review)
                           ↓
                    Expert Corrects?
                      /          \
                    YES           NO
                     ↓             ↓
            Corrective RAG    System Learns
            (Learn from fix)   Pattern
                     ↓             ↓
              Update FUTURE   Improve Metrics
              Predictions
```

---

## Component 1: Expert Analyzer - Automatic Flagging

**File:** `expert_analyzer.py`

### Purpose
Identifies cases that need human review before submission. Automatically flags:
- Low confidence classifications
- Novel crime patterns not in training data
- Conflicting signals between stages
- Metrics validation failures
- Rare crime combinations

### Key Features

#### 7 Flagging Reasons:
```python
LOW_CONFIDENCE          # <0.70 confidence
NOVEL_PATTERN          # Pattern not seen before
CONFLICTING_SIGNALS    # Stages disagree
NEW_CRIME_TYPE         # Unknown crime category
RARE_COMBINATION       # Uncommon indicator mix
METRIC_THRESHOLD_MISS  # Validation failures
AMBIGUOUS_INDICATORS   # Weak pattern signals
CROSS_CATEGORY         # Multi-type suggestion
```

#### 3-Tier Severity Levels:
```
HIGH     → Critical cases needing immediate review
MEDIUM   → Important cases needing review
LOW      → Cases worth monitoring
```

### Usage

```python
from expert_analyzer import expert_analyzer

# Analyze classification for expert review
flag = await expert_analyzer.analyze_for_flagging(
    classification_result=classifier_result,
    incident_description=user_input,
    stage_outputs=classifier_result["stages"]
)

if flag:
    print(f"⚠️  Case flagged as {flag.severity}: {flag.reason.value}")
    print(f"Supporting evidence: {flag.supporting_evidence}")
    print(f"Alternative interpretations: {flag.alternative_types}")
    
    # Case goes to expert queue for review
    await expert_queue.add(flag)

# Get pending expert reviews
pending = expert_analyzer.get_pending_expert_reviews()
print(f"Cases awaiting review: {pending['pending_count']}")

# Get coverage analysis
coverage = expert_analyzer.get_case_coverage_report()
print(f"Well-covered types: {[t for t, s in coverage['coverage_by_type'].items() if s['coverage_level'] == 'WELL_COVERED']}")
print(f"Coverage gaps: {coverage['coverage_gaps']}")
```

### Data Tracked
- Cases flagged for review
- Reasons for flagging
- Expert determinations
- Crime type coverage statistics
- Pattern diversity metrics

---

## Component 2: Corrective RAG - Learning from Corrections

**File:** `corrective_rag.py`

### Purpose
System learns from human corrections to improve future predictions. When experts correct a misclassification, that knowledge is applied to similar cases.

### How It Works

**Step 1: Human Correction**
```
System predicts: "fraud" (confidence: 0.65)
Expert corrects: "Identity Theft"
Reason: "Account opened in victim's name"
```

**Step 2: Correction Recording**
```python
from corrective_rag import corrective_rag

await corrective_rag.record_correction(
    case_id="case_001",
    original_prediction="fraud",
    corrected_prediction="identity_theft",
    confidence_before=0.65,
    incident_description="My account was opened...",
    feedback_reason="Account opened in victim's name"
)
```

**Step 3: Future Application**
```
New incident: "Someone opened an account..."
System initially predicts: "fraud" (0.68)

Corrective RAG finds similar correction:
- Case fraud→identity_theft (similarity: 0.82)
- Applies penalty to fraud: 0.68 → 0.55
- Boosts identity_theft: 0.15 → 0.30

Final prediction: "identity_theft" (0.30 → 0.35 range)
```

### Key Methods

#### 1. Record Corrections
```python
result = await corrective_rag.record_correction(
    case_id="case_001",
    original_prediction="fraud",
    corrected_prediction="identity_theft",
    confidence_before=0.65,
    incident_description="...",
    feedback_reason="..."
)
# Returns: {"success": True, "correction_weight": 1.5, "pattern_frequency": 2}
```

#### 2. Apply Boosting to Predictions
```python
current_predictions = {
    "fraud": 0.68,
    "identity_theft": 0.15,
    "phishing": 0.10,
    "ransomware": 0.07
}

boosted = await corrective_rag.apply_corrective_boosting(
    current_prediction="fraud",
    all_predictions=current_predictions,
    incident_description="..."
)
# Returns adjusted predictions with learned corrections applied
```

#### 3. Analyze Error Patterns
```python
error_patterns = corrective_rag.get_common_error_patterns()
# Returns: {
#   "total_corrections": 15,
#   "unique_patterns": 8,
#   "patterns": [
#     {
#       "pattern": "fraud → identity_theft",
#       "frequency": 5,
#       "avg_wrong_confidence": 0.62,
#       "common_reasons": {"account opened": 4, "credit damage": 1}
#     },
#     ...
#   ]
# }
```

#### 4. Get Learning Progress
```python
progress = corrective_rag.get_learning_progress()
# Returns learning strength, error rates per type, retraining recommendations
```

### Correction Weight System
```
Impact = 1.0 - confidence_before
Weight = Impact × 1.5 (capped at 2.0)

Example:
- Wrong with 0.95 confidence → High learning value (weight: 1.5)
- Wrong with 0.50 confidence → Lower learning value (weight: 0.5)
```

---

## Component 3: Self-RAG - Self-Validation

**File:** `self_rag.py`

### Purpose
System validates its own predictions through 5 checkpoint system before submission. Can suggest revisions or request human review.

### Five Validation Checkpoints

#### 1. **Internal Consistency**
```
Check: Do all 4 stages agree on prediction?
Pass: 2+ stages agree
Delta: +0.1 if pass, -0.1 if fail
Example: If Stage1→fraud, Stage2→fraud, Stage3→fraud
Result: ✓ Pass (consistent)
```

#### 2. **Knowledge Grounding**
```
Check: Are there similar known cases?
Pass: At least 1 case with same crime type
Delta: +0.05 to +0.15 based on case count
Example: If 5 known "phishing" cases exist
Result: ✓ Pass (well-grounded pattern)
```

#### 3. **Confidence Calibration**
```
Check: Is reported confidence justified by uncertainty?
Pass: Confidence within stage confidence ranges
Delta: +0.05 if well-calibrated, -0.1 if overconfident
Example: Stage gap=0.15, reported conf=0.90
Result: ✗ Fail (overconfident given stage uncertainty)
```

#### 4. **Edge Case Detection**
```
Check: Are crime-specific indicators present?
Pass: At least 1 crime-specific keyword found
Delta: +0.05 if present, -0.08 if missing
Example: Phishing prediction but no "verify"/"click"/"credentials"
Result: ✗ Fail (weak edge case evidence)
```

#### 5. **Cross-Domain Validation**
```
Check: Does RAG consensus agree?
Pass: Similar cases support prediction
Delta: +0.10 if supported, -0.15 if contradicted
Example: Predict "fraud" but 4/5 similar cases are "identity_theft"
Result: ✗ Fail (contradicted by cases)
```

### Usage

```python
from self_rag import self_rag

# Validate the prediction
validation = await self_rag.validate_prediction(
    prediction="fraud",
    confidence=0.85,
    stage_outputs=classifier["stages"],
    incident_description="..."
)

# Check results
print(f"Original: {validation['original_prediction']} ({validation['original_confidence']:.2%})")
print(f"Checkpoints passed: {validation['checkpoints_passed']}/{validation['total_checkpoints']}")

for cp in validation['validation_checkpoints']:
    status = "✓" if cp['passed'] else "✗"
    print(f"{status} {cp['name']}: {cp['reasoning']}")
    print(f"   Confidence delta: {cp['confidence_delta']:+.3f}")

print(f"Adjusted confidence: {validation['adjusted_confidence']:.2%}")
print(f"Recommendation: {validation['recommendation']}")

if validation['needs_revision']:
    print(f"Revision needed: {validation['revision_suggestion']}")
```

### Confidence Adjustment Flow
```
Original Confidence: 0.85
  ↓
Internal Consistency Check:     ✓ +0.10 (0.95)
Knowledge Grounding Check:      ✓ +0.10 (1.05 → cap at 0.99)
Confidence Calibration Check:   ✗ -0.10 (0.89)
Edge Case Detection Check:      ✓ +0.05 (0.94)
Cross-Domain Validation Check:  ✓ +0.10 (1.04 → cap at 0.99)
  ↓
Adjusted Confidence: 0.94
Recommendation: SUBMIT - High confidence, validation successful
```

---

## Complete Integration Flow

### End-to-End Process

```
User Submits Incident
        ↓
[Crime Classifier V3]
  ├─ Stage 1: Semantic Router
  ├─ Stage 2: Hierarchical
  ├─ Stage 3: Pattern Matcher
  └─ Stage 4: RAG Retriever
        ↓
Result → [Self-RAG Validation]
  ├─ Internal Consistency
  ├─ Knowledge Grounding
  ├─ Confidence Calibration
  ├─ Edge Case Detection
  └─ Cross-Domain Validation
        ↓
    ┌───Validation Passed?
    │        ├─ YES ──→ [Expert Flagging]
    │        │             ├─ Low Confidence?
    │        │             ├─ Novel Pattern?
    │        │             ├─ Conflicting Signals?
    │        │             └─ Other Issues?
    │        │
    │        └─ NO ──→ System Loss of Confidence
    │              Skip Expert Flagging
    ↓
Confidence > 0.80?
  ├─ YES ──→ AUTO SUBMIT
  └─ NO  ──→ HUMAN REVIEW QUEUE
        ↓
Human Reviews Case
  ├─ Accepts System Prediction
  │    └─[Expert Analyzer] Updates Coverage Stats
  │
  └─ Corrects System Prediction
       └─[Corrective RAG] Records Correction
           └─ Applies to Similar Cases
           └─ Analyzes Error Patterns
           └─ Recommends Retraining if Needed
```

---

## Advanced Usage Examples

### Example 1: Complete Classification with Learning

```python
from crime_classifier_v3 import crime_classifier_v3
from self_rag import self_rag
from expert_analyzer import expert_analyzer
from corrective_rag import corrective_rag

# Step 1: Get classification
result = await crime_classifier_v3.classify_incident(
    user_input="I received an email asking to verify my Bank account..."
)

# Step 2: Self-validate
validation = await self_rag.validate_prediction(
    prediction=result["final_prediction"],
    confidence=result["final_confidence"],
    stage_outputs=result["stages"],
    incident_description=user_input
)

# Step 3: Check if needs expert review
expert_flag = await expert_analyzer.analyze_for_flagging(
    classification_result=result,
    incident_description=user_input,
    stage_outputs=result["stages"]
)

# Step 4: Decision logic
if expert_flag:
    # Flag for human review
    await expert_queue.add(expert_flag)
    status = "PENDING_REVIEW"
else:
    # Auto-submit if confident
    if validation["adjusted_confidence"] > 0.80:
        status = "AUTO_SUBMITTED"
    else:
        status = "HUMAN_REVIEW"

# Step 5: If expert corrects the classification
if expert_corrects:
    await corrective_rag.record_correction(
        case_id=result["case_id"],
        original_prediction=result["final_prediction"],
        corrected_prediction=expert_determination,
        confidence_before=result["final_confidence"],
        incident_description=user_input,
        feedback_reason=expert_feedback_text
    )
```

### Example 2: Monitor Learning Progress

```python
# Check how much the system has learned
progress = corrective_rag.get_learning_progress()
print(f"Learning strength: {progress['learning_strength']}")
print(f"Total corrections learned: {progress['total_corrections_learned']}")
print(f"Error patterns discovered: {progress['unique_patterns_learned']}")

# Identify biggest issues
error_patterns = corrective_rag.get_common_error_patterns()
for pattern in error_patterns["patterns"][:3]:
    print(f"Issue: {pattern['pattern']} (occurred {pattern['frequency']} times)")

# Check if retraining needed
retrain = corrective_rag.recommend_retraining()
if retrain:
    print(f"⚠️  RECOMMEND RETRAINING: {retrain['reason']}")
    print(f"Priority: {retrain['priority']}")

# Check coverage gaps
coverage = expert_analyzer.get_case_coverage_report()
print(f"Crime types needing more data: {coverage['coverage_gaps']}")

# Validation statistics
stats = self_rag.get_validation_statistics()
print(f"Revisions suggested in {stats['revision_rate']:.1f}% of cases")
print(f"Confidence improved by avg {stats['confidence_improvement']:.3f}")
```

### Example 3: Adaptive Classification with Learning

```python
# Use corrective boosting in new predictions
current_predictions = {
    "fraud": 0.72,
    "identity_theft": 0.12,
    "phishing": 0.10,
    "other": 0.06
}

# Apply what we've learned from corrections
boosted = await corrective_rag.apply_corrective_boosting(
    current_prediction="fraud",
    all_predictions=current_predictions,
    incident_description=new_incident
)

print(f"Before learning: fraud={current_predictions['fraud']:.2%}")
print(f"After learning:  fraud={boosted['boosted_predictions']['fraud']:.2%}")
print(f"Corrections applied: {boosted['corrections_applied']}")
```

---

## Data Persistence & Optimization

### Storage Strategy

**In-Memory (Session):**
- Current classifications
- Corrections in current session
- Validation history

**Persistent (Vector DB):**
- All cases stored in `correlation_engine.case_database`
- Case embeddings cached in RAG retriever
- Historical patterns in pattern matcher

### Optimization Tips

1. **Clear Memory for Fresh Start:**
   ```python
   expert_analyzer.flagged_cases = []
   corrective_rag.corrections = []
   self_rag.validation_history = []
   ```

2. **Archive Old Learning Data:**
   ```python
   # Archive corrections older than 30 days
   old_corrections = [c for c in corrective_rag.corrections 
                      if (datetime.now() - datetime.fromisoformat(c.correction_timestamp)).days > 30]
   corrective_rag.corrections = [c for c in corrective_rag.corrections 
                                  if (datetime.now() - datetime.fromisoformat(c.correction_timestamp)).days <= 30]
   ```

3. **Batch Import Corrections:**
   ```python
   # If migrating from another system
   for correction_data in legacy_corrections:
       await corrective_rag.record_correction(
           case_id=correction_data["id"],
           original_prediction=correction_data["wrong"],
           corrected_prediction=correction_data["right"],
           confidence_before=correction_data["confidence"],
           incident_description=correction_data["text"],
           feedback_reason=correction_data["reason"]
       )
   ```

---

## Key Metrics to Monitor

### System Health Dashboard
```
Learning System Status:
  ├─ Expert Flagging
  │  ├─ Cases flagged this session: 3
  │  ├─ Pending expert review: 2
  │  └─ Most common flag reason: CONFLICTING_SIGNALS
  │
  ├─ Corrective RAG
  │  ├─ Total corrections learned: 12
  │  ├─ Unique error patterns: 6
  │  ├─ Learning strength: MODERATE
  │  └─ Recommend retraining: YES (P=HIGH)
  │
  ├─ Self-RAG Validation
  │  ├─ Avg checkpoints passed: 4.2/5
  │  ├─ Revisions suggested: 18.5%
  │  ├─ Confidence improvement: +0.035
  │  └─ Recommendation rate: 60% SUBMIT, 40% REVIEW
  │
  └─ Crime Type Coverage
     ├─ Well-covered types: 8
     ├─ Sparse coverage: 2
     └─ Coverage gaps: none
```

---

## Next Steps

1. **Session 1** ✅ Create learning components
2. **Session 2** - Integrate into main.py
3. **Session 3** - Create feedback API endpoints
4. **Session 4** - Add retraining mechanism
5. **Session 5** - Deploy to production monitoring

