# Workload Predictor - Statistical Model in R
# This script builds models to predict how long assignments will take

# Install required packages if not present
if (!require("tidyverse")) install.packages("tidyverse")
if (!require("caret")) install.packages("caret")

library(tidyverse)
library(caret)

# Function to train workload prediction model
train_workload_model <- function(historical_data) {
  """
  Train a linear regression model on historical assignment data
  
  Args:
    historical_data: data frame with columns:
      - assignment_type: character (essay, project, exam, reading, other)
      - priority: numeric (1-5)
      - estimated_hours: numeric (initial estimate)
      - actual_hours: numeric (actual time spent)
      - grade: numeric (0-100, optional)
  
  Returns:
    list with model and preprocessing info
  """
  
  # Return NULL if no data
  if (nrow(historical_data) == 0) {
    return(list(
      model = NULL,
      error = "No historical data provided"
    ))
  }
  
  # Prepare data
  data <- historical_data %>%
    mutate(
      # Numeric encoding of assignment type
      type_numeric = case_when(
        assignment_type == "exam" ~ 5,
        assignment_type == "project" ~ 4,
        assignment_type == "essay" ~ 3,
        assignment_type == "reading" ~ 2,
        TRUE ~ 1
      ),
      # Calculate estimation accuracy
      estimation_ratio = actual_hours / estimated_hours,
      # Grade impact (higher grades = possibly more time spent)
      grade_normalized = grade / 100
    )
  
  # Train linear regression model
  model <- lm(actual_hours ~ type_numeric + priority + estimated_hours + grade_normalized, 
              data = data)
  
  return(list(
    model = model,
    success = TRUE,
    n_observations = nrow(data),
    r_squared = summary(model)$r.squared,
    coefficients = coef(model)
  ))
}

# Function to predict workload for a new assignment
predict_workload <- function(model, new_assignment) {
  """
  Predict how long a new assignment will take
  
  Args:
    model: trained model from train_workload_model
    new_assignment: data frame with columns:
      - assignment_type: character
      - priority: numeric (1-5)
      - estimated_hours: numeric
      - grade: numeric (default 85 if not provided)
  
  Returns:
    list with prediction and confidence interval
  """
  
  if (is.null(model)) {
    return(list(
      error = "Model not trained",
      prediction = NA,
      confidence_low = NA,
      confidence_high = NA
    ))
  }
  
  # Prepare new data
  new_data <- new_assignment %>%
    mutate(
      assignment_type = as.character(assignment_type),
      type_numeric = case_when(
        assignment_type == "exam" ~ 5,
        assignment_type == "project" ~ 4,
        assignment_type == "essay" ~ 3,
        assignment_type == "reading" ~ 2,
        TRUE ~ 1
      ),
      grade = if_else(is.na(grade), 85, grade),
      grade_normalized = grade / 100
    )
  
  # Make prediction with confidence interval
  pred <- predict(model, 
                  newdata = new_data, 
                  interval = "confidence",
                  level = 0.95)
  
  # Ensure prediction is positive
  predicted_hours <- max(0.5, pred[1, 1])  # Minimum 30 minutes
  confidence_low <- max(0.5, pred[1, 2])
  confidence_high <- pred[1, 3]
  
  return(list(
    success = TRUE,
    predicted_hours = round(predicted_hours, 1),
    confidence_low = round(confidence_low, 1),
    confidence_high = round(confidence_high, 1),
    confidence_interval = sprintf("%.1f - %.1f hours", confidence_low, confidence_high)
  ))
}

# Alternative: GLM model for time category prediction (easy, medium, hard)
train_workload_classifier <- function(historical_data) {
  """
  Train a logistic regression model to classify assignments into time categories
  
  Args:
    historical_data: data frame with assignment data
  
  Returns:
    list with classification model
  """
  
  if (nrow(historical_data) == 0) {
    return(list(model = NULL, error = "No historical data"))
  }
  
  # Create time categories based on actual hours
  data <- historical_data %>%
    mutate(
      type_numeric = case_when(
        assignment_type == "exam" ~ 5,
        assignment_type == "project" ~ 4,
        assignment_type == "essay" ~ 3,
        assignment_type == "reading" ~ 2,
        TRUE ~ 1
      ),
      grade = if_else(is.na(grade), 85, grade),
      grade_normalized = grade / 100,
      # Categorize by quartiles
      time_category = cut(actual_hours, 
                         breaks = quantile(actual_hours, probs = c(0, 0.33, 0.67, 1)),
                         labels = c("quick", "medium", "lengthy"),
                         include.lowest = TRUE)
    )
  
  # Train multinomial logistic regression
  model <- glm(time_category ~ type_numeric + priority + estimated_hours + grade_normalized,
               data = data,
               family = "multinomial")
  
  return(list(
    model = model,
    success = TRUE,
    n_observations = nrow(data),
    categories = c("quick", "medium", "lengthy")
  ))
}

# Function to suggest optimal scheduling based on workload predictions
suggest_schedule <- function(predicted_hours, priority) {
  """
  Suggest when to work on assignment based on predicted hours and priority
  
  Args:
    predicted_hours: numeric, predicted time needed
    priority: numeric (1-5)
  
  Returns:
    list with scheduling recommendation
  """
  
  days_ahead <- case_when(
    priority == 5 ~ 7,        # Start 1 week before
    priority == 4 ~ 5,        # Start 5 days before
    priority == 3 ~ 3,        # Start 3 days before
    priority == 2 ~ 2,        # Start 2 days before
    TRUE ~ 1                  # Start 1 day before
  )
  
  # Suggest session lengths
  session_length <- case_when(
    predicted_hours <= 2 ~ 1.5,
    predicted_hours <= 5 ~ 2,
    predicted_hours <= 10 ~ 2.5,
    TRUE ~ 3
  )
  
  num_sessions <- ceiling(predicted_hours / session_length)
  
  return(list(
    days_to_start = days_ahead,
    session_length = session_length,
    num_sessions = num_sessions,
    recommendation = sprintf(
      "Start %d days before deadline. Plan %d sessions of %.1f hours each",
      days_ahead,
      num_sessions,
      session_length
    )
  ))
}

# Export functions for use with rpy2
