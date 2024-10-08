from pdf2image import convert_from_path
import fitz
import base64
from PIL import Image
import io
import requests
import re
import os

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

   

