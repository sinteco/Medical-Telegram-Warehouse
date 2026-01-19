from fastapi import FastAPI

app = FastAPI(title="Medical Data Warehouse API")

@app.get("/")
async def root():
    return {"message": "Welcome to the Medical Data Warehouse API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
