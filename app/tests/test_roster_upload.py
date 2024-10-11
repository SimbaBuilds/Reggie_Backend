import io
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.endpoints import digitization  # Import the module, not the app



# Create a mock FastAPI app
mock_app = FastAPI()
mock_app.post("/upload/student-csv")(digitization.upload_student_csv)
mock_app.post("/upload/staff-csv")(digitization.upload_staff_csv)

client = TestClient(mock_app)

@pytest.fixture
def mock_current_user():
    return MagicMock(organization_name="Test Org")

@pytest.fixture
def mock_supabase():
    mock = MagicMock()
    mock.table().select().eq().execute.return_value.data = [{"id": "test-org-id"}]
    mock.table().insert().execute.return_value = MagicMock()
    return mock

@patch("app.endpoints.digitization.get_current_user")
@patch("app.endpoints.digitization.get_db")
@patch("app.endpoints.digitization.map_csv_headers")
def test_upload_student_csv(mock_map_headers, mock_get_db, mock_get_current_user, mock_current_user, mock_supabase):
    mock_get_current_user.return_value = mock_current_user
    mock_get_db.return_value = mock_supabase
    mock_map_headers.return_value = {
        "First Name": "first_name",
        "Last Name": "last_name",
        "DOB": "date_of_birth",
        "Grade Level": "grade"
    }

    csv_content = "First Name,Last Name,DOB,Grade Level\nJohn,Doe,2000-01-01,9\nJane,Smith,2001-02-02,10"
    files = {"file": ("students.csv", io.StringIO(csv_content))}

    response = client.post("/upload/student-csv", files=files)

    assert response.status_code == 200
    assert response.json()["message"] == "Student CSV uploaded and processed successfully"
    assert response.json()["rows_processed"] == 2

@patch("app.endpoints.digitization.get_current_user")
@patch("app.endpoints.digitization.get_db")
@patch("app.endpoints.digitization.map_csv_headers")
def test_upload_staff_csv(mock_map_headers, mock_get_db, mock_get_current_user, mock_current_user, mock_supabase):
    mock_get_current_user.return_value = mock_current_user
    mock_get_db.return_value = mock_supabase
    mock_map_headers.return_value = {
        "First Name": "first_name",
        "Last Name": "last_name",
        "Date of Birth": "date_of_birth"
    }

    csv_content = "First Name,Last Name,Date of Birth\nJohn,Doe,1980-01-01\nJane,Smith,1985-02-02"
    files = {"file": ("staff.csv", io.StringIO(csv_content))}

    response = client.post("/upload/staff-csv", files=files)

    assert response.status_code == 200
    assert response.json()["message"] == "Staff CSV uploaded and processed successfully"
    assert response.json()["rows_processed"] == 2

def test_upload_invalid_csv():
    invalid_csv = "Invalid,CSV,Content\nThis,is,not,valid"
    files = {"file": ("invalid.csv", io.StringIO(invalid_csv))}

    response = client.post("/upload/student-csv", files=files)

    assert response.status_code == 400
    assert "Error processing CSV" in response.json()["detail"]

@patch("app.endpoints.digitization.get_current_user")
@patch("app.endpoints.digitization.get_db")
@patch("app.endpoints.digitization.map_csv_headers")
def test_upload_csv_missing_required_columns(mock_map_headers, mock_get_db, mock_get_current_user, mock_current_user, mock_supabase):
    mock_get_current_user.return_value = mock_current_user
    mock_get_db.return_value = mock_supabase
    mock_map_headers.return_value = {
        "First Name": "first_name",
        "Last Name": "last_name"
    }

    csv_content = "First Name,Last Name\nJohn,Doe\nJane,Smith"
    files = {"file": ("students.csv", io.StringIO(csv_content))}

    response = client.post("/upload/student-csv", files=files)

    assert response.status_code == 400
    assert "Missing required columns" in response.json()["detail"]

@patch("app.endpoints.digitization.get_current_user")
@patch("app.endpoints.digitization.get_db")
@patch("app.endpoints.digitization.map_csv_headers")
def test_upload_csv_extra_columns(mock_map_headers, mock_get_db, mock_get_current_user, mock_current_user, mock_supabase):
    mock_get_current_user.return_value = mock_current_user
    mock_get_db.return_value = mock_supabase
    mock_map_headers.return_value = {
        "First Name": "first_name",
        "Last Name": "last_name",
        "DOB": "date_of_birth",
        "Grade Level": "grade",
        "Extra Column": None
    }

    csv_content = "First Name,Last Name,DOB,Grade Level,Extra Column\nJohn,Doe,2000-01-01,9,Extra"
    files = {"file": ("students.csv", io.StringIO(csv_content))}

    response = client.post("/upload/student-csv", files=files)

    assert response.status_code == 200
    assert response.json()["message"] == "Student CSV uploaded and processed successfully"
    assert response.json()["rows_processed"] == 1

def test_upload_empty_csv():
    empty_csv = ""
    files = {"file": ("empty.csv", io.StringIO(empty_csv))}

    response = client.post("/upload/student-csv", files=files)

    assert response.status_code == 400
    assert "Empty CSV file" in response.json()["detail"]

@patch("app.endpoints.digitization.get_current_user")
@patch("app.endpoints.digitization.get_db")
@patch("app.endpoints.digitization.map_csv_headers")
def test_upload_large_csv(mock_map_headers, mock_get_db, mock_get_current_user, mock_current_user, mock_supabase):
    mock_get_current_user.return_value = mock_current_user
    mock_get_db.return_value = mock_supabase
    mock_map_headers.return_value = {
        "First Name": "first_name",
        "Last Name": "last_name",
        "DOB": "date_of_birth",
        "Grade Level": "grade"
    }

    # Generate a large CSV with 10,000 rows
    csv_content = "First Name,Last Name,DOB,Grade Level\n"
    csv_content += "John,Doe,2000-01-01,9\n" * 10000
    files = {"file": ("large_students.csv", io.StringIO(csv_content))}

    response = client.post("/upload/student-csv", files=files)

    assert response.status_code == 200
    assert response.json()["message"] == "Student CSV uploaded and processed successfully"
    assert response.json()["rows_processed"] == 10000

@patch("app.endpoints.digitization.get_current_user")
@patch("app.endpoints.digitization.get_db")
@patch("app.endpoints.digitization.map_csv_headers")
def test_database_insert_failure(mock_map_headers, mock_get_db, mock_get_current_user, mock_current_user, mock_supabase):
    mock_get_current_user.return_value = mock_current_user
    mock_get_db.return_value = mock_supabase
    mock_map_headers.return_value = {
        "First Name": "first_name",
        "Last Name": "last_name",
        "DOB": "date_of_birth",
        "Grade Level": "grade"
    }

    # Simulate a database insert failure
    mock_supabase.table().insert().execute.side_effect = Exception("Database insert failed")

    csv_content = "First Name,Last Name,DOB,Grade Level\nJohn,Doe,2000-01-01,9"
    files = {"file": ("students.csv", io.StringIO(csv_content))}

    response = client.post("/upload/student-csv", files=files)

    assert response.status_code == 500
    assert "Error inserting data into database" in response.json()["detail"]

# Add more tests as needed
