"""Workload Predictor - Python wrapper for R statistical models"""
import os
import json
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import pandas as pd

try:
    import rpy2
    from rpy2.robjects import r, pandas2ri
    from rpy2.robjects.packages import importr
    R_AVAILABLE = True
except ImportError:
    R_AVAILABLE = False
    print("Warning: rpy2 not installed. Workload predictor will use fallback model.")

# Enable R to pandas conversion
if R_AVAILABLE:
    pandas2ri.activate()


class WorkloadPredictor:
    """
    Machine learning model for predicting assignment workload using R statistical models.
    Falls back to simple heuristic if R is not available.
    """
    
    def __init__(self):
        """Initialize the workload predictor"""
        self.model = None
        self.historical_data = []
        self.r_available = R_AVAILABLE
        self.script_path = os.path.join(
            os.path.dirname(__file__),
            'workload_predictor.R'
        )
        self._load_r_script()
    
    def _load_r_script(self):
        """Load the R script into the R environment"""
        if not self.r_available:
            return
        
        try:
            if os.path.exists(self.script_path):
                r.source(self.script_path)
        except Exception as e:
            print(f"Warning: Could not load R script: {e}")
            self.r_available = False
    
    def train_model(self, historical_assignments: List[Dict]) -> Dict:
        """
        Train the workload prediction model on historical data
        
        Args:
            historical_assignments: List of dicts with:
                - assignment_type: str (essay, project, exam, reading, other)
                - priority: int (1-5)
                - estimated_hours: float
                - actual_hours: float (actual time spent)
                - grade: float (0-100, optional)
        
        Returns:
            Training result with model stats
        """
        if not historical_assignments:
            return {"error": "No historical data provided"}
        
        self.historical_data = historical_assignments
        
        if not self.r_available:
            return {
                "success": True,
                "method": "fallback",
                "n_observations": len(historical_assignments),
                "message": "Using heuristic model (R not available)"
            }
        
        try:
            # Convert to pandas DataFrame
            df = pd.DataFrame(historical_assignments)
            
            # Call R function
            result = r.train_workload_model(df)
            
            return {
                "success": True,
                "method": "r_linear_regression",
                "n_observations": result[4],  # n_observations index
                "r_squared": float(result[3]),  # r_squared index
                "message": "Model trained successfully"
            }
        except Exception as e:
            return {
                "error": str(e),
                "fallback": True,
                "method": "heuristic"
            }
    
    def predict_workload(self, assignment: Dict) -> Dict:
        """
        Predict how long an assignment will take
        
        Args:
            assignment: Dict with:
                - assignment_type: str
                - priority: int (1-5)
                - estimated_hours: float
                - grade: float (optional, default 85)
                - description: str (optional, for fallback method)
        
        Returns:
            Prediction dict with:
                - predicted_hours: float
                - confidence_low: float
                - confidence_high: float
                - recommendation: str
        """
        
        # Use R model if available and trained
        if self.r_available and self.historical_data:
            try:
                df = pd.DataFrame([assignment])
                result = r.predict_workload(self.model, df)
                
                prediction = {
                    "predicted_hours": float(result[1]),  # predicted_hours index
                    "confidence_low": float(result[2]),
                    "confidence_high": float(result[3]),
                    "confidence_interval": result[4],
                    "method": "r_linear_regression"
                }
            except Exception as e:
                # Fallback on error
                prediction = self._fallback_predict(assignment)
                prediction["error"] = str(e)
        else:
            # Use fallback heuristic
            prediction = self._fallback_predict(assignment)
        
        # Add scheduling recommendation
        prediction["scheduling"] = self._suggest_schedule(
            prediction.get("predicted_hours", assignment.get("estimated_hours", 5)),
            assignment.get("priority", 3)
        )
        
        return prediction
    
    def _fallback_predict(self, assignment: Dict) -> Dict:
        """
        Fallback heuristic prediction when R is not available
        Based on assignment type, priority, and estimated hours
        """
        
        assignment_type = assignment.get("assignment_type", "other").lower()
        priority = assignment.get("priority", 3)
        estimated = assignment.get("estimated_hours", 5)
        
        # Type multipliers (historical averages)
        type_multipliers = {
            "exam": 1.2,
            "project": 1.15,
            "essay": 1.1,
            "reading": 0.95,
            "other": 1.0
        }
        
        multiplier = type_multipliers.get(assignment_type, 1.0)
        
        # Priority adjustment
        priority_adjustment = 1 + (priority - 3) * 0.1  # ±10% per priority level
        
        # Predicted hours
        predicted = estimated * multiplier * priority_adjustment
        predicted = max(0.5, min(predicted, 50))  # Clamp between 30 min and 50 hours
        
        # Confidence interval (wider for heuristic)
        confidence_range = estimated * 0.4  # ±40% of estimated
        
        return {
            "predicted_hours": round(predicted, 1),
            "confidence_low": round(max(0.5, predicted - confidence_range), 1),
            "confidence_high": round(predicted + confidence_range, 1),
            "confidence_interval": f"{round(predicted - confidence_range, 1):.1f} - {round(predicted + confidence_range, 1):.1f} hours",
            "method": "heuristic_fallback"
        }
    
    def _suggest_schedule(self, predicted_hours: float, priority: int) -> Dict:
        """
        Suggest optimal scheduling for the assignment
        
        Args:
            predicted_hours: predicted time needed
            priority: assignment priority (1-5)
        
        Returns:
            Scheduling recommendation
        """
        
        # Days before deadline to start
        days_map = {5: 7, 4: 5, 3: 3, 2: 2, 1: 1}
        days_ahead = days_map.get(priority, 3)
        
        # Session length based on total hours
        if predicted_hours <= 2:
            session_length = 1.5
        elif predicted_hours <= 5:
            session_length = 2.0
        elif predicted_hours <= 10:
            session_length = 2.5
        else:
            session_length = 3.0
        
        num_sessions = max(1, round(predicted_hours / session_length))
        
        # Calculate dates
        start_date = datetime.now() + timedelta(days=-days_ahead)
        
        return {
            "days_to_start": days_ahead,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "session_length_hours": session_length,
            "num_sessions": num_sessions,
            "recommendation": (
                f"Start {days_ahead} day{'s' if days_ahead != 1 else ''} before deadline. "
                f"Plan {num_sessions} session{'s' if num_sessions != 1 else ''} "
                f"of {session_length:.1f} hours each."
            )
        }
    
    def batch_predict(self, assignments: List[Dict]) -> List[Dict]:
        """
        Predict workload for multiple assignments
        
        Args:
            assignments: List of assignment dicts
        
        Returns:
            List of predictions
        """
        return [self.predict_workload(a) for a in assignments]
    
    def get_model_stats(self) -> Dict:
        """Get statistics about the trained model"""
        if not self.historical_data:
            return {
                "trained": False,
                "message": "No model trained yet"
            }
        
        return {
            "trained": True,
            "method": "r_linear_regression" if self.r_available else "heuristic",
            "n_observations": len(self.historical_data),
            "r_available": self.r_available
        }


# Global predictor instance
_predictor = None

def get_predictor() -> WorkloadPredictor:
    """Get or create the global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = WorkloadPredictor()
    return _predictor
