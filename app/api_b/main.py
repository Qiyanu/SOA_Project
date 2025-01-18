from fastapi import FastAPI
from app.api_b.routes import router

# Initialize FastAPI app
app = FastAPI(
    title="Train Filtering API",
    description="API to filter and retrieve available trains based on various criteria such as stations, dates, seat class, and availability.",
    version="1.0",
    contact={
        "name": "API Support",
        "url": "https://example.com/contact",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Include routes
app.include_router(router)
