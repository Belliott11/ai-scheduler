# Workload Predictor

A machine learning component that predicts how long assignments will take using R statistical models.

## Overview

The Workload Predictor analyzes historical assignment data and builds predictive models to forecast the time required for new assignments. It uses R's statistical capabilities for robust predictions and falls back to a heuristic method if R is unavailable.

### Key Features

- **Statistical Modeling**: Linear regression models built with R's `lm()` function
- **Intelligent Predictions**: Considers assignment type, priority, estimated hours, and grades
- **Confidence Intervals**: Provides uncertainty estimates (95% confidence level)
- **Smart Scheduling**: Recommends when to start and how to break up the work
- **Fallback System**: Works with heuristic predictions if R is unavailable
- **Batch Processing**: Predict for multiple assignments at once

## Architecture

### Components

1. **R Script** (`backend/services/workload_predictor.R`)
   - Statistical models using `lm()` for regression
   - Data preprocessing and feature engineering
   - Scheduling optimization logic

2. **Python Wrapper** (`backend/services/workload_predictor.py`)
   - Bridges Python and R using rpy2
   - Graceful fallback to heuristics if R unavailable
   - Session management and caching

3. **FastAPI Endpoints** (`backend/main.py`)
   - Training endpoint
   - Single and batch prediction endpoints
   - Model statistics endpoint

## API Endpoints

### Train the Model

```http
POST /workload/train
Content-Type: application/json

{
  "historical_assignments": [
    {
      "assignment_type": "essay",
      "priority": 4,
      "estimated_hours": 5.0,
      "actual_hours": 6.5,
      "grade": 92.0
    },
    {
      "assignment_type": "project",
      "priority": 5,
      "estimated_hours": 10.0,
      "actual_hours": 11.2,
      "grade": 88.5
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "method": "r_linear_regression",
  "n_observations": 2,
  "r_squared": 0.87,
  "message": "Model trained successfully"
}
```

### Predict Workload

```http
POST /workload/predict
Content-Type: application/json

{
  "assignment": {
    "assignment_type": "essay",
    "priority": 4,
    "estimated_hours": 5.0,
    "grade": 85.0
  }
}
```

**Response:**
```json
{
  "success": true,
  "assignment": {
    "assignment_type": "essay",
    "priority": 4,
    "estimated_hours": 5.0,
    "grade": 85.0
  },
  "prediction": {
    "predicted_hours": 5.8,
    "confidence_low": 4.2,
    "confidence_high": 7.4,
    "confidence_interval": "4.2 - 7.4 hours",
    "method": "r_linear_regression",
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

### Batch Predict

```http
POST /workload/batch-predict
Content-Type: application/json

{
  "assignments": [
    {"assignment_type": "essay", "priority": 4, "estimated_hours": 5.0},
    {"assignment_type": "exam", "priority": 5, "estimated_hours": 8.0},
    {"assignment_type": "reading", "priority": 2, "estimated_hours": 2.0}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "predictions": [
    {
      "assignment": {...},
      "prediction": {...}
    },
    ...
  ]
}
```

### Get Model Stats

```http
GET /workload/stats
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "trained": true,
    "method": "r_linear_regression",
    "n_observations": 15,
    "r_available": true
  }
}
```

## Model Details

### Features Used

The model considers the following features:

| Feature | Type | Description |
| --- | --- | --- |
| `assignment_type` | categorical | essay, project, exam, reading, other |
| `priority` | numeric | 1-5 scale, higher = more important |
| `estimated_hours` | numeric | Initial estimate by student/instructor |
| `grade` | numeric | 0-100 scale, optional |

### Feature Engineering

1. **Type Encoding**: Converted to numeric values (reading=2, essay=3, project=4, exam=5)
2. **Estimation Ratio**: Actual hours / Estimated hours
3. **Grade Normalization**: Grade / 100 (0-1 scale)

### Model Formula

```r
actual_hours ~ type_numeric + priority + estimated_hours + grade_normalized
```

### Interpretation

Example coefficients (varies with data):
- **type_numeric**: 0.35 (each type level adds ~20 min)
- **priority**: 0.25 (each priority level adds ~15 min)
- **estimated_hours**: 0.85 (estimates are 85% accurate)
- **grade_normalized**: 0.5 (higher grades correlate with slightly more time)

## Installation & Setup

### Requirements

```bash
# For Python only (uses fallback heuristic):
pip install -r requirements.txt

# For full R integration:
# 1. Install R from https://www.r-project.org/
# 2. Install required R packages:
Rscript -e "install.packages(c('tidyverse', 'caret'))"

# 3. Uncomment rpy2 in requirements.txt:
pip install rpy2==3.17.0
```

### Verify Setup

```bash
# Check if R integration is available:
curl http://localhost:8000/workload/stats

# Should show:
{
  "stats": {
    "r_available": true  # or false if R not installed
  }
}
```

## Usage Examples

### Frontend Integration

```javascript
// Train the model
const historicalData = [
  { assignment_type: 'essay', priority: 4, estimated_hours: 5, actual_hours: 6.5, grade: 92 },
  { assignment_type: 'project', priority: 5, estimated_hours: 10, actual_hours: 11.2, grade: 88 }
];

const trainResult = await api.trainWorkloadPredictor(historicalData);
console.log(`Model trained with ${trainResult.stats.n_observations} observations`);

// Predict for new assignment
const newAssignment = {
  assignment_type: 'essay',
  priority: 4,
  estimated_hours: 5.0
};

const prediction = await api.predictWorkload(newAssignment);
console.log(`This essay will likely take ${prediction.prediction.predicted_hours} hours`);
console.log(prediction.prediction.scheduling.recommendation);

// Batch predict
const assignments = [
  { assignment_type: 'essay', priority: 4, estimated_hours: 5 },
  { assignment_type: 'exam', priority: 5, estimated_hours: 8 }
];

const results = await api.batchPredictWorkload(assignments);
results.predictions.forEach(p => {
  console.log(`${p.assignment.assignment_type}: ${p.prediction.predicted_hours} hours`);
});
```

### Python Integration

```python
from backend.services.workload_predictor import get_predictor

# Get predictor instance
predictor = get_predictor()

# Train with historical data
historical = [
    {
        'assignment_type': 'essay',
        'priority': 4,
        'estimated_hours': 5.0,
        'actual_hours': 6.5,
        'grade': 92.0
    }
]
predictor.train_model(historical)

# Predict for new assignment
assignment = {
    'assignment_type': 'essay',
    'priority': 4,
    'estimated_hours': 5.0
}
prediction = predictor.predict_workload(assignment)
print(f"Predicted: {prediction['predicted_hours']} hours")
print(f"Confidence: {prediction['confidence_interval']}")
print(prediction['scheduling']['recommendation'])
```

## How It Works

### Training Phase

1. **Collect Historical Data**: Past assignments with actual hours and grades
2. **Feature Engineering**: Convert categorical variables to numeric
3. **Model Fitting**: Linear regression to learn relationships
4. **Validation**: Calculate R² and confidence intervals

### Prediction Phase

1. **Feature Extraction**: Convert new assignment data to model features
2. **Prediction**: Use linear regression to forecast hours
3. **Confidence Interval**: Calculate 95% CI for uncertainty estimate
4. **Scheduling**: Recommend start date and session structure

## Accuracy & Limitations

### Accuracy Factors

- **Data Quality**: More varied historical data = better predictions
- **Assignment Similarity**: Works best for similar assignment types
- **External Factors**: Doesn't account for illness, major events, etc.

### Limitations

1. **Requires Training Data**: Needs at least 3-5 historical assignments to train
2. **Individual Variation**: One student's pace ≠ another's
3. **Context Not Captured**: Can't account for unforeseen circumstances
4. **Course-Specific**: Model is specific to the individual student/course

### Fallback Heuristic

If R is unavailable, predictions use this formula:

```
predicted_hours = estimated_hours × type_multiplier × priority_adjustment

type_multiplier:
  - exam: 1.2 (typically take 20% longer)
  - project: 1.15
  - essay: 1.1
  - reading: 0.95 (typically faster than estimate)
  - other: 1.0

priority_adjustment: 1 + (priority - 3) × 0.1
  - priority 5: ×1.2 (20% longer)
  - priority 3: ×1.0 (as estimated)
  - priority 1: ×0.8 (20% shorter)
```

## Best Practices

### Getting Accurate Predictions

1. **Provide Good Estimates**: Initial estimates should be realistic
2. **Log Actual Time**: Record actual hours spent on each assignment
3. **Include Grades**: Helps model account for quality impact
4. **Collect Variety**: Include different assignment types and priorities
5. **Periodic Retraining**: Retrain model as you complete more assignments

### Using Predictions

1. **Not Absolute**: Treat as probability, not certainty
2. **Add Buffer**: Add 20-30% for unforeseen issues
3. **Adjust Schedules**: Use as basis for schedule generation
4. **Track Accuracy**: Compare predictions vs. actual to improve
5. **Context Matters**: Consider course difficulty, your workload, etc.

## Troubleshooting

### R Not Found

**Error**: `Warning: rpy2 not installed. Workload predictor will use fallback model.`

**Solution**:
1. Install R: https://www.r-project.org/
2. Install R packages:
   ```bash
   Rscript -e "install.packages(c('tidyverse', 'caret'))"
   ```
3. Uncomment rpy2 in requirements.txt
4. Reinstall Python packages: `pip install -r requirements.txt`

### Model Not Training

**Error**: `error: "No historical data provided"`

**Solution**: Ensure you're sending historical assignments with:
- `assignment_type`: Valid type (essay, project, exam, reading, other)
- `priority`: Number between 1-5
- `estimated_hours`: Positive float
- `actual_hours`: Positive float (time actually spent)

### Predictions Seem Wrong

**Solution**:
1. Check `method` in response (should be `r_linear_regression`, not `heuristic_fallback`)
2. Check `stats` endpoint - ensure `r_available: true`
3. Verify training data quality and quantity (need at least 5 samples)
4. Look at `confidence_interval` - wide intervals mean lower confidence

## Future Enhancements

- [ ] Time-series forecasting (account for trends over semester)
- [ ] Multi-course models (predict across courses)
- [ ] Generalized models (share data between students)
- [ ] Neural networks for non-linear patterns
- [ ] Real-time accuracy tracking
- [ ] A/B testing different scheduling strategies
- [ ] Integration with calendar (detect busy periods)
- [ ] Adjustment factors (sleep deprivation, other courses, etc.)

## References

### R Functions Used

- `lm()` - Linear regression model
- `glm()` - Generalized linear models
- `predict()` - Make predictions with confidence intervals
- `caret` - Machine learning utilities

### Papers

- Linear regression: [Wikipedia](https://en.wikipedia.org/wiki/Linear_regression)
- Prediction intervals: [R Documentation](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/predict.lm.html)
- Machine learning workflow: Kuhn & Johnson (2013) - Applied Predictive Modeling

## API Status

**Current Version**: 1.0.0

| Method | Endpoint | Status |
| --- | --- | --- |
| POST | `/workload/train` | ✅ Available |
| POST | `/workload/predict` | ✅ Available |
| POST | `/workload/batch-predict` | ✅ Available |
| GET | `/workload/stats` | ✅ Available |
