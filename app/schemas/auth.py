from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class SignupResponse(BaseModel):
    user: UserResponse
    message: str

class LogoutResponse(BaseModel):
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str 