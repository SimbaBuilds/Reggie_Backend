from pydantic import BaseModel
from typing import List

class Person(BaseModel):
    id: int
    first_name: str
    last_name: str

class StudentListResponse(BaseModel):
    students: List[Person]

class StaffListResponse(BaseModel):
    staff: List[Person]

class UpdateResponse(BaseModel):
    message: str

class AddPersonResponse(BaseModel):
    person_id: int
    message: str

class RemovePersonResponse(BaseModel):
    message: str