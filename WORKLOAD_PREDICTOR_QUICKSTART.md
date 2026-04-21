# Workload Predictor Quick Start

## 5-Minute Setup

### 1. Install R (Optional but Recommended)

For full statistical modeling power:

**Windows**:
- Download from https://www.r-project.org/
- Run installer with default settings

**macOS**:
```bash
brew install r
```

**Linux**:
```bash
sudo apt-get install r-base
```

### 2. Install R Packages

```bash
Rscript -e "install.packages(c('tidyverse', 'caret'))"
```

### 3. Enable rpy2 in Python

Uncomment in `backend/requirements.txt`:
```
rpy2==3.17.0
```

Then install:
```bash
pip install -r requirements.txt
```

### 4. Test Installation

```bash
# Start backend
python main.py

# In another terminal, test:
curl http://localhost:8000/workload/stats
```

Should return:
```json
{
  "success": true,
  "stats": {
    "r_available": true,
    "trained": false
  }
}
```

## Usage Examples

### Example 1: Train Model with Past Assignments

```bash
curl -X POST http://localhost:8000/workload/train \
  -H "Content-Type: application/json" \
  -d '{
    "historical_assignments": [
      {
        "assignment_type": "essay",
        "priority": 4,
        "estimated_hours": 5,
        "actual_hours": 6.5,
        "grade": 92
      },
      {
        "assignment_type": "project",
        "priority": 5,
        "estimated_hours": 10,
        "actual_hours": 11.2,
        "grade": 88
      },
      {
        "assignment_type": "reading",
        "priority": 2,
        "estimated_hours": 2,
        "actual_hours": 1.8,
        "grade": 95
      }
    ]
  }'
```

**Response**:
```json
{
  "success": true,
  "method": "r_linear_regression",
  "n_observations": 3,
  "r_squared": 0.95,
  "message": "Model trained successfully"
}
```

### Example 2: Predict New Assignment

```bash
curl -X POST http://localhost:8000/workload/predict \
  -H "Content-Type: application/json" \
  -d '{
    "assignment": {
      "assignment_type": "essay",
      "priority": 4,
      "estimated_hours": 5
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "prediction": {
    "predicted_hours": 6.2,
    "confidence_low": 5.1,
    "confidence_high": 7.3,
    "confidence_interval": "5.1 - 7.3 hours",
    "scheduling": {
      "days_to_start": 3,
      "start_date": "2024-04-17",
      "session_length_hours": 2.0,
      "num_sessions": 3,
      "recommendation": "Start 3 days before deadline. Plan 3 sessions of 2.0 hours each."
    }
  }
}
```

### Example 3: Batch Predict Multiple Assignments

```bash
curl -X POST http://localhost:8000/workload/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "assignments": [
      {
        "assignment_type": "essay",
        "priority": 4,
        "estimated_hours": 5
      },
      {
        "assignment_type": "exam",
        "priority": 5,
        "estimated_hours": 8
      },
      {
        "assignment_type": "reading",
        "priority": 2,
        "estimated_hours": 2
      }
    ]
  }'
```

## Without R (Fallback Mode)

If R is not installed, the predictor uses a heuristic model:

```json
{
  "predicted_hours": 5.5,
  "method": "heuristic_fallback"
}
```

This still provides reasonable estimates based on:
- Assignment type multipliers
- Priority adjustments
- Historical norms

See [WORKLOAD_PREDICTOR.md](../WORKLOAD_PREDICTOR.md) for the fallback formula.

## Integration with Schedule Generator

Use predictions to improve schedule generation:

```javascript
// 1. Train predictor with past assignments
await api.trainWorkloadPredictor(historicalAssignments);

// 2. Get workload predictions for syllabus assignments
const predictions = await api.batchPredictWorkload(assignments);

// 3. Update estimated_hours with predictions
assignments = assignments.map((a, i) => ({
  ...a,
  estimated_hours: predictions[i].prediction.predicted_hours
}));

// 4. Generate schedule with improved estimates
await api.createSchedule(sessionId);
```

## Collecting Data for Your Model

### Keep Track Of:
1. **Assignment details**:
   - Type (essay, project, exam, reading)
   - Priority/importance
   - Your initial estimate

2. **Actual time spent**:
   - Use a timer or time tracker
   - Log daily
   - Include all related activities

3. **Grades** (optional):
   - Final grade/score
   - Helps model understand quality vs. time

### Data Collection Template

```
Assignment | Type | Priority | Estimate | Actual | Grade
-----------|------|----------|----------|--------|-------
Essay 1    | essay| 4        | 5 hrs    | 6.5    | 92%
Lab Report | project| 5      | 10 hrs   | 11.2   | 88%
Reading    | reading| 2      | 2 hrs    | 1.8    | 95%
```

## Tips for Better Predictions

1. **Start with 5-10 assignments** to train
2. **Variety helps**: Include different types and priorities
3. **Be honest**: Track actual time, not "perfect" time
4. **Update regularly**: Retrain every 10-15 assignments
5. **Review accuracy**: Compare predictions vs. actual

## Troubleshooting

### Error: "Model not trained"
- Call `/workload/train` endpoint first with historical data
- Send at least 3 past assignments

### Error: "rpy2 not installed"
1. Install R from https://www.r-project.org/
2. Run: `Rscript -e "install.packages(c('tidyverse', 'caret'))"`
3. Uncomment rpy2 in requirements.txt
4. Run: `pip install -r requirements.txt`
5. Restart backend

### Predictions seem off
- Check confidence interval - wide means low confidence
- Make sure historical data matches new assignments
- Retrain with more diverse data

## Next Steps

- Read [WORKLOAD_PREDICTOR.md](../WORKLOAD_PREDICTOR.md) for detailed documentation
- Integrate predictions into your schedule generator
- Use scheduling recommendations to plan better
- Track prediction accuracy over time

## Questions?

Check these resources:
- [WORKLOAD_PREDICTOR.md](../WORKLOAD_PREDICTOR.md) - Full documentation
- [README.md](../README.md) - Project overview
- [DEPLOYMENT.md](../DEPLOYMENT.md) - Deployment guide
