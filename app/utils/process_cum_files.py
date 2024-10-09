import os
import base64
from googleapiclient.http import MediaFileUpload
import json
try:
    from utils.process_page import find_best_match
    from app.utils.process_page import pdf_page_to_base64, process_image
    from utils.create_mapping import create_mapping
except ModuleNotFoundError:
    from app.utils.process_page import find_best_match
    from app.utils.process_page import pdf_page_to_base64, process_image
    from app.utils.create_mapping import create_mapping
import csv
import json
import shutil
import os
import base64
from googleapiclient.errors import HttpError






# Function to get the gmail label ID by name
def get_label_id(service, label_name):
    try:
        # Retrieve all the labels in the Gmail account
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        print("Email labels retrieved")
        # Find the label with the given name and return its ID
        for label in labels:
            if label['name'] == label_name:
                return label['id']
        
        print(f"Label '{label_name}' not found.")
        return None
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_unread_student_record_emails(gmail_service, email_label_name):
    label_name = email_label_name  
    label_id = get_label_id(gmail_service, label_name)
    
    if label_id:
        try:
            # Add both labelId for "UNREAD" and the custom label
            response = gmail_service.users().messages().list(
                userId='me', 
                labelIds=[label_id, 'UNREAD']
            ).execute()
            
            messages = response.get('messages', [])
            print(f"num messages found: {len(messages)}, {messages}")
            return messages
        except HttpError as error:
            print(f"An error occurred: {error}")
            return
    else:
        print(f"Label '{label_name}' not found.")
        return

def download_attachments(message_id, gmail_service):
    message = gmail_service.users().messages().get(userId='me', id=message_id).execute()
    saved_files = []
    
    for part in message['payload'].get('parts', []):
        if part['filename'] and part['filename'].endswith('.pdf'):
            attachment = gmail_service.users().messages().attachments().get(
                userId='me', 
                messageId=message_id, 
                id=part['body']['attachmentId']
            ).execute()
            
            data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
            path = f"./downloads/{part['filename']}"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'wb') as f:
                f.write(data)
                
            saved_files.append(path)
    
    if not saved_files:
        print("No PDF attachments found.")
        
    return saved_files


def create_list_of_students(csv_path):

    with open(csv_path, mode='r') as file:
        reader = csv.DictReader(file)
        
        # Create a list of formatted strings
        formatted_list = [f"{row['Last Name']}_{row['First Name']}_{row['Birthdate']}" for row in reader]


    list_of_lists = [formatted.split('_') for formatted in formatted_list]

    return list_of_lists

# Extract student name using Tesseract OCR
def extract_student_name(pdf_path, csv_path):

    b64 = pdf_page_to_base64(pdf_path)

    listified_student = process_image(b64) 
    # listified_student = ['Van', 'Domas', '10/08/09'] #for testing

    listified_student[0] = listified_student[0].lower().capitalize()
    listified_student[1] = listified_student[1].lower().capitalize()

    list_of_students = create_list_of_students(csv_path)  #list of lists

    best_match, score, item = find_best_match(listified_student, list_of_students)


    return best_match, score, item

# Create or find folder in Google Drive
def create_or_find_folder(folder_name, drive_service,parent_id=None,):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, spaces='drive').execute()
    files = results.get('files', [])
    if files:
        print(f"Folder found: {folder_name}")
        return files[0]['id']  # Return existing folder ID
    # If folder doesn't exist, create it
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id] if parent_id else []
    }
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    print(f"Folder created: {folder_name}")
    return folder['id']

def find_folder_by_name(service, folder_name, parent_id=None):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)', pageSize=1).execute()
    folders = results.get('files', [])
    
    if len(folders) > 0:
        return folders[0]['id']
    else:
        return None


# Upload PDF to student folder in the cohort
def upload_to_student_folder(student_name, cohort, pdf_path, drive_service, root_folder_id):
    # Find or create the cohort folder
    cohort_folder_id = create_or_find_folder(cohort, drive_service, parent_id=root_folder_id)
    # Find or create the student's folder
    student_folder_id = create_or_find_folder(student_name, drive_service, parent_id=cohort_folder_id)
    # Upload the PDF
    file_metadata = {
        'name': os.path.basename(pdf_path),
        'parents': [student_folder_id]
    }
    media = MediaFileUpload(pdf_path, mimetype='application/pdf')
    drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("file added to folder")   

# Load the student mapping from the JSON file
with open('student_mapping.json', 'r') as json_file:
    student_mapping = json.load(json_file)

def mark_as_read(label_name, gmail_service):
    label_id = get_label_id(gmail_service, label_name)
    
    if label_id:
        try:
            # Get all unread emails under the specified label
            response = gmail_service.users().messages().list(
                userId='me', 
                labelIds=[label_id, 'UNREAD']
            ).execute()
            
            messages = response.get('messages', [])
            
            if not messages:
                print("No unread emails found.")
                return
            
            for message in messages:
                msg_id = message['id']
                # Mark email as read by removing the 'UNREAD' label
                gmail_service.users().messages().modify(
                    userId='me', 
                    id=msg_id, 
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                
            print(f"Marked {len(messages)} emails as read.")
        except HttpError as error:
            print(f"An error occurred: {error}")
    else:
        print(f"Label '{label_name}' not found.")

def write_list_to_json(no_match_list, filename='unmatched.json'):
    # Create a list of dictionaries with meaningful keys
    data = [
        {"Last Name": sublist[0], "First Name": sublist[1], "DOB": sublist[2], "pdf_path": sublist[3]}
        for sublist in no_match_list
    ]

    # Write to JSON file
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"Unmatched list written to written to {filename}")

def delete_downloads_folder():
    downloads_folder = './downloads'
    if os.path.exists(downloads_folder):
        shutil.rmtree(downloads_folder)

def process_hundred_messages(creds, gmail_service, drive_service, email_label_name, root_drive_folder_name, csv_path):
    messages = get_unread_student_record_emails(gmail_service, email_label_name)
    no_match_list = []
    create_mapping(csv_path)
    for i in range(len(messages)):
        print(f"\n\n\nIter: {i + 1}")
        pdf_paths = download_attachments(messages[i]['id'], gmail_service)
        for pdf_path in pdf_paths:
            # Extract the student name from the PDF
            best_match, score, item = extract_student_name(pdf_path, csv_path)
            if best_match == "no match":
                print(f"No match found for {item}, score: {score}, pdf: {pdf_path}")
                item.append(pdf_path)
                no_match_list.append(item)
                continue
            else:
                student_name = f"{best_match[0]}_{best_match[1]}"
                print(f"Match found with name: {item}, score: {score}")
            
            # Retrieve the cohort from the JSON file
            cohort = student_mapping.get(student_name)
            def escape_single_quotes(input_string):
                return input_string.replace("'", "\\'")
            processed_name = escape_single_quotes(student_name)

            if cohort:
                # Upload the PDF to the appropriate student folder
                root_folder_id = find_folder_by_name(drive_service, folder_name=root_drive_folder_name)
                print("root folder found with id: ", root_folder_id)
                upload_to_student_folder(processed_name, cohort, pdf_path, drive_service, root_folder_id)
            else:
                print(f"Mapping not found for {student_name}")
        print(f"Attachments with no match:{no_match_list}\n\n\n")
    mark_as_read(email_label_name, gmail_service)
    delete_downloads_folder()
    write_list_to_json(no_match_list)


