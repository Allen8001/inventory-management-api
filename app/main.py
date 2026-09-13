from fastapi import FastAPI

from app.api.product_routes import router as product_router

app = FastAPI(
    title="Inventory Management API",
    version="0.1.0",
)

app.include_router(product_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}