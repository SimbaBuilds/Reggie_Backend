from pdf2image import convert_from_path
import fitz
import base64
from PIL import Image
import io
import requests
import re
import os
from difflib import SequenceMatcher


api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")



def pdf_page_to_base64(pdf_path):
    pages = convert_from_path(pdf_path, first_page=0, last_page=1)
    image_path = "page_image.jpg"
    pages[0].save(image_path, 'JPEG')

    doc = fitz.open(pdf_path)
    page = doc[0]
    # Convert the PDF page to a PIL Image object
    pix = page.get_pixmap()
    img_bytes = pix.tobytes("jpeg")
    img = Image.open(io.BytesIO(img_bytes))
    
    # Convert the PIL Image to base64
    buffered = io.BytesIO()
    img.save(buffered, format="jpeg")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    return img_base64


def process_image(b64):

    prompt = """
    Extract the student first name, last name,and date of birth from the image.  
    The student last name is printed above Student Name (last), the student first name is printed above (first).  
    Date of birth is printed above Date of birth right below Student Name (last).
    Output in the format lastname_firstname_mm/dd/year delimitted by triple backticks.
    Make sure single digit months and days are formatted as 0X.
    """


    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4o",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{b64}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_json = response.json()  # Convert the response to a dictionary
    content = response_json['choices'][0]['message']['content']


    try:
        parsed_text = re.search(r'```(.*?)```', content, re.DOTALL).group(1).strip()
    except AttributeError:
        parsed_text = None  # or handle the error in another appropriate way

    if parsed_text is None:
        print("No text found in pdf")
        return ['', '', '']
    
    listified_student = parsed_text.split('_')

    return listified_student


def get_similarity_score(item1, item2):
    """Calculates a similarity score between two strings."""
    return SequenceMatcher(None, item1, item2).ratio()

def find_best_match(item, list_of_items):
    best_match = None
    best_score = 0
    min_score_threshold = 1.5  # Out of 3, adjust as needed, lower means more matches


    for candidate in list_of_items:
        # Calculate similarity score for each corresponding part (last name, first name, DOB)
        last_name_score = get_similarity_score(item[0], candidate[0])
        first_name_score = get_similarity_score(item[1], candidate[1])
        dob_match = candidate[2] == item[2]
        if dob_match:    
            dob_score = 1
        else:
            dob_score = 0
        
        # Add scores together
        total_score = last_name_score + first_name_score + dob_score
        

        # Update the best match if this one has a higher score
        if total_score > best_score:
            best_match = candidate
            best_score = total_score
    
    # Check if the best score meets the minimum threshold
    if best_score >= min_score_threshold:
        return best_match, best_score, item
    else:
        return "no match", best_score, item


