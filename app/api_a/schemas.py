from pydantic import BaseModel

# Schema for user registration
class RegisterUserRequest(BaseModel):
    username: str
    password: str

# Schema for user authentication
class AuthenticateUserRequest(BaseModel):
    username: str
    password: str
