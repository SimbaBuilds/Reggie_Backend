#Current File Structure
# REGGIE_BACKEND
REGGIE_BACKEND/
│
├── __pycache__/
│   └── app/
│
├── app/
│   ├── __pycache__/
│   │   ├── __init__.cpython-311.pyc
│   │   └── main.cpython-311.pyc
│   ├── api/
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── assistant.py
│   │       ├── auth.py
│   │       ├── cover_pages.py
│   │       ├── digitization.py
│   │       ├── email_automation.py
│   │       ├── email_templates.py
│   │       ├── file_management.py
│   │       ├── files.py
│   │       ├── gmail_webhook.py
│   │       ├── roster_management.py
│   │       ├── settings.py
│   │       └── stats.py
│
├── core/
│
├── db/
│
├── schemas/
│
├── services/
│   ├── drive_service.py
│   ├── gmail_service.py
│   └── roster_service.py
│
├── utils/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── authenticate.py
│   ├── create_mapping.py
│   ├── get_name_from_registrar.py
│   ├── gmail_utils.py
│   ├── handle_misc_records.py
│   ├── process_cum_files.py
│   ├── process_page.py
│   ├── thread_store.py
├── main.py
├── models.py