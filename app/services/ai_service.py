from typing import List
from openai import OpenAI
from app.core.config import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)

def map_csv_headers(headers: List[str], csv_type: str) -> dict:
    """
    Use a small AI model to map CSV headers to standardized fields,
    handling variations in header names for both staff and student CSVs.
    """
    standard_fields = "first_name, last_name, date_of_birth"
    if csv_type.lower() == "student":
        standard_fields += ", grade"

    prompt = f"""
    Map the following {csv_type} CSV headers to these standard fields:
    {standard_fields}

    CSV headers: {', '.join(headers)}

    Provide the mapping in a 'original: mapped' format, one per line.
    If a standard field is missing, don't include it in the output.
    """
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that maps CSV headers to standard fields."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Parse the AI response to create a mapping dictionary
        mapping = {}
        content = completion.choices[0].message.content
        for line in content.split('\n'):
            if ':' in line:
                original, mapped = line.split(':', 1)
                mapping[original.strip()] = mapped.strip()
        
        return mapping
    except Exception as e:
        # Log the error and re-raise or handle as appropriate
        print(f"An error occurred: {str(e)}")
        raise