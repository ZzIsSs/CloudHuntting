from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.s4_content.routes import router as content_router
import uvicorn

app = FastAPI(
    title="Service 4: Content & CSKH",
    description="Microservice managing Posts, News, Reviews, and Customer Support Tickets",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(content_router, prefix="/api/v1")

@app.get("/", tags=["System"])
def root():
    """Root endpoint to verify the service is responding."""
    return {"message": "Welcome to Service 4: Content & CSKH"}

@app.get("/health", tags=["System"])
def health_check():
    """Check if the service is up and running."""
    return {"status": "ok", "service": "s4_content"}

if __name__ == "__main__":
    uvicorn.run("src.s4_content.main:app", host="127.0.0.1", port=8004, reload=True)
