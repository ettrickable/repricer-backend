from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from other web apps (like Streamlit frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Accept requests from any origin (safe for now)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Repricer API is running"}

@app.get("/test")
def test():
    return {"success": True, "note": "This is a test endpoint"}
