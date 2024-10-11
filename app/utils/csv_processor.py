import pandas as pd
from typing import Dict

def process_csv(df: pd.DataFrame, mapped_headers: Dict[str, str], csv_type: str) -> pd.DataFrame:
    """
    Process the CSV DataFrame using the mapped headers for either staff or students.
    """
    # Create a reverse mapping for easier column renaming
    reverse_mapping = {v: k for k, v in mapped_headers.items()}
    
    # Rename columns based on the mapped headers
    df = df.rename(columns=reverse_mapping)
    
    # Define required columns based on CSV type
    required_columns = ['first_name', 'last_name', 'date_of_birth']
    if csv_type.lower() == "student":
        required_columns.append('grade')
    
    # Ensure required columns are present
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Required column(s) {', '.join(missing_columns)} are missing from the {csv_type} CSV")
    
    # Standardize date_of_birth format (assuming it's in a recognizable date format)
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # Process grade for students
    if csv_type.lower() == "student":
        # Ensure grade is a string (in case it's numeric in the CSV)
        df['grade'] = df['grade'].astype(str)
    elif 'grade' in df.columns:
        # Remove grade column if present in staff CSV
        df = df.drop(columns=['grade'])
    
    # Additional processing can be added here (e.g., data validation, formatting)
    
    return df