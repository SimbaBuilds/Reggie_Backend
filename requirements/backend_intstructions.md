#Project Overview
I am building a web applicaiton called Reggie that is a software product that will speed up workflows in the education admin space.
This is the back end of the applicaiton built in Python and FastAPI.
Marketing quotes:
"No more jam-packed file rooms"
“No 4 month lead time -- have your records digitized as soon as you can scan them"


#Core Functionalities
The back end of the application will do the follwing:
1. Digitize a school's pdf records.  The set up process for digitization will include the following:
    a. A person list csv will come from the front end -- a small AI model will be used to map to correct headers to decrease need for user header naming precision
    b. Identify person associated with record and further process their record.  
        i. If the user selects a "consistent first page" option, a user generated natural language description will be used to help an AI enabled vision model tag the person.
        ii. If the "cover page" option is used, simple OCR will be used to tag the person.
    c. A matching algorithm is used to determine if their is a sufficient match.  If there is a sufficient match, the record will be further processed, if not, details of the record will be sent back to the front end to be displayed to the user.
    d. A transcript batch of all student's transcripts will come from the frontend and transcripts will automatically be added to students' drive folders
2. Organize and upload digitized records to the cloud -- folders are found or created.  Parent folder name "Student Records" for students and "Staff Records" for staff.
3. A series of email assistant automations will be set up for the customer utilizing watch functions linked to their email that act when an email is assigned a label.  Email labels are as follows:
    a. Cumulative Files -- this email label will handle the initial digitization process as well as the creation of new persons in the system post digitization -- it is able to handle multiple attachemnts in one email as well as attachments spread across multiple emails within or not wihtin the same thread.
    b. Miscellaneous Labeled Records -- this email label will handle incoming records in bulk like state test scores, but these records must be labeled with a cover page with first, last, and DOB
    c. Miscellaneous Unlabeled Records -- this email label will handle incoming miscellaneous student records -- it will only be able to handle one record at a time, and the suer will be prompted with an email from reggie asking for the person first, last, and DOB
    d. Records Request -- an email in this label will trigger an auto draft response email containing student records and current transcript

4. Users will need to update the person roster via email to Reggie or via the application user interface.



#Docs
FastAPI, Google Mail (GMAIL), Google Drive, Google Auth, OpenAI


#Current File Structure

REGGIE_BACKEND
├── __pycache__
├── app
│   ├── __pycache__
│   └── endpoints
│       ├── __pycache__
│       ├── __init__.py
│       └── gmail_webhook.py
├── utils
│   ├── __pycache__
│   ├── __init__.py
│   ├── authenticate.py
│   ├── create_mapping.py
│   ├── fetch_unread.py
│   ├── get_best_match.py
│   ├── get_name_from_registrar.py
│   ├── gmail_utils.py
│   ├── process_cum_files.py
│   ├── process_first_page.py
│   ├── process_misc_records.py
│   ├── test_thread_store.py
│   └── thread_store.py
├── __init__.py
├── main.py
├── schemas.py
├── dev
├── node_modules
├── requirements
│   └── backend_instructions.md
├── venv
│   ├── bin
│   ├── include
│   └── lib
├── pyenv.cfg
├── .env
├── .gitignore
└── credentials.json