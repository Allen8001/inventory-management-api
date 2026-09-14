from fastapi import FastAPI

from app.api.product_routes import router as product_router


tags_metadata = [
    {
        "name": "Products",
        "description": "Create, retrieve, update and delete products.",
    },
    {
        "name": "System",
        "description": "System health and service monitoring endpoints.",
    },
]


app = FastAPI(
    title="Inventory Management API",
    description=(
        "RESTful backend service for product and inventory management, "
        "built with FastAPI, SQLAlchemy and MySQL."
    ),
    version="0.1.0",
    openapi_tags=tags_metadata,
)

app.include_router(product_router)


@app.get(
    "/health",
    tags=["System"],
)
def health_check():
    return {"status": "ok"}