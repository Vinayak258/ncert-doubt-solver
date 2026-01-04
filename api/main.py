from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .routes import query

# Load env
load_dotenv()

app = FastAPI(
    title="NCERT Doubt Solver API",
    description="Gateway API for the Student Doubt Solver",
    version="1.0.0"
)

# CORS Configuration
# Allow all for local dev/hackathon convenience
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(query.router, prefix="/api", tags=["Chat"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "api_gateway"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
