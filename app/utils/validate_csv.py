import pandas as pd
from typing import List, Dict

def validate_csv(df: pd.DataFrame, required_columns: List[str], csv_type: str) -> Dict[str, bool | str]:
    # Check for empty CSV
    if df.empty:
        return {"is_valid": False, "error": "The CSV file is empty."}
    
    # Check for missing required columns
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        return {"is_valid": False, "error": f"Missing required columns: {', '.join(missing_columns)}"}
    
    # Check for unexpected columns
    extra_columns = set(df.columns) - set(required_columns)
    if extra_columns:
        return {"is_valid": False, "error": f"Unexpected columns found: {', '.join(extra_columns)}"}
    
    # Check for very large CSVs (e.g., more than 10,000 rows)
    if len(df) > 10000:
        return {"is_valid": False, "error": "CSV file is too large. Maximum allowed rows: 10,000"}
    
    # Add more specific validations based on csv_type if needed
    if csv_type == "student":
        # Example: Validate grade column
        if not df['grade'].apply(lambda x: str(x).isdigit()).all():
            return {"is_valid": False, "error": "Invalid grade values. Grades must be numeric."}
    
    return {"is_valid": True, "error": ""}
