from fastapi import FastAPI, UploadFile, File
from typing import List

app = FastAPI(title="NIDM API", version="0.1")

@app.get("/")
def root():
    return {"message": "NIDM backend running"}

@app.post("/ingest/text")
def ingest_text(narrative: str):
    return {"status": "received", "length": len(narrative)}

@app.post("/ingest/file")
async def ingest_file(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}

@app.get("/simulate")
def simulate():
    return {"result": "simulation placeholder"}
