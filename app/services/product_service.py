from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate


class ProductAlreadyExistsError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class ProductService:

    def __init__(self, repository: ProductRepository | None = None):
        self.repository = repository or ProductRepository()

    def create_product(
        self,
        db: Session,
        product_data: ProductCreate,
    ) -> Product:
        existing_product = self.repository.get_by_sku(
            db,
            product_data.sku,
        )

        if existing_product is not None:
            raise ProductAlreadyExistsError(
                f"Product with SKU '{product_data.sku}' already exists."
            )

        product = Product(
            **product_data.model_dump()
        )

        try:
            self.repository.add(db, product)
            db.commit()
            db.refresh(product)
        except Exception:
            db.rollback()
            raise

        return product

    def get_product_by_id(
        self,
        db: Session,
        product_id: int,
    ) -> Product:
        product = self.repository.get_by_id(
            db,
            product_id,
        )

        if product is None:
            raise ProductNotFoundError(
                f"Product with ID {product_id} was not found."
            )

        return product