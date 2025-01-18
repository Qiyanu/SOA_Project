from fastapi import FastAPI
from app.api_a.routes import router

app = FastAPI(
    title="Client Authentication API",
    description="API to manage user registration and authentication.",
    version="1.0.0",
)

# Include routes
app.include_router(router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Client Authentication API"}
