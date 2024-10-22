#Core Functionalities
The back end of the application will do the following:
1. Digitize a school's pdf records.  The set up process for digitization will include the following:
    1. A student list csv and optional staff list csv will come from the front end -- a small AI model will be used to map to correct headers to decrease need for user header naming precision
    2. A specific Google Drive folder structure will be created for the user inside their google drive based on the student csv and optional staff csv they uploaded 
    3. Identify person associated with record and further process their record.  
        1. If the user selects a "consistent first page" option, a user generated natural language description will be used to help an AI enabled vision model tag the person.
        2. If the "cover page" option is used, simple OCR will be used to tag the person.

    3. A matching algorithm is used to determine if there is a sufficient match.  If there is a sufficient match, the record will be further processed, if not, details of the record will be sent back to the front end to be displayed to the user.

    5. If a users records are already digitized, option to manually organize (with Drive folder structure created for them) so that Reggie can use.


2. Organize and upload digitized records to the cloud -- folders are found or created.  Parent folder name "Student Records" for students and "Staff Records" for staff.
    1. Use datetime to map current grade level to cohort
    3. Small org versus large org logic to ensure user in correct payment plan (from roster count)

3. A transcript batch of all student's transcripts will come from the frontend and transcripts will automatically be added to students' drive folders
    1. Use gpt-4o-mini to process first n characters and find name and DOB and output with OpenAI API structured output
    2. Handle two page transcripts
    3. Logic for including transcripts in records requests - app file storage or store in drive folders and handle duplicates upon semester re-upload

4. A series of email assistant automations will be set up for the customer utilizing watch functions linked to their email that act when an email is assigned a label.  Email labels created for them via API?  Email labels are as follows:
    1. Cumulative Files -- this email label will handle the initial digitization process as well as the creation of new persons in the system post digitization -- it is able to handle multiple attachemnts in one email as well as attachments spread across multiple emails within or not wihtin the same thread.
    2. Miscellaneous Labeled Records -- this email label will handle incoming records in bulk like state test scores, but these records must be labeled with a cover page with first, last, and DOB -- auto rename the attachment
    3. Miscellaneous Unlabeled Records -- this email label will handle incoming miscellaneous student records -- it will only be able to handle one record at a time, and the suer will be prompted with an email from reggie asking for the person first, last, and DOB
    4. Records Request -- an email in this label will trigger an auto draft response email containing student records and current transcript
    5. Template Response -- an email in this trigger will trigger a response using a user template -- templates and descritpions can be uploaded by the user in the app
        1. Max 8 template emails


5. Users will need to update the person roster via email to Reggie or via the application user interface.
    1. Internal logic to use date of birth to determine whether person should be added to student list or staff list

6. Reggie will be able to able to receive email messages containing csv files or google sheet links from users and perform requested edits and additions 
    1. Prospective users will get 10 emails with Reggie before being prompted to sign up for a plan 
    2. Will need to incorporate code interpreter in a sandbox environment as well as internal AI review checks that the user defined tasks have been completed correctly
    3. Reggie will get link to sheet from hyperlink or full link in email 
    4. If user asks question outside of Reggie's scope, he will still try to be helpful
    5. Reggie can only add to a sheet or create a new sheet - no deletions 


7. Other Features
    1. Max 5 users per organization
    2. Free tier: file structure built for you and 5 Reggie actions per user per week
    3. Need more tiers for large districts
