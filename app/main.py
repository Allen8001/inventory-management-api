from fastapi import FastAPI

app = FastAPI(
    title="Inventoru  Management API",
        version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}