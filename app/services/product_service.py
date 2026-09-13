from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


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

    def get_products(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
        )

    def update_product(
        self,
        db: Session,
        product_id: int,
        product_data: ProductUpdate,
    ) -> Product:
        product = self.repository.get_by_id(
            db,
            product_id,
        )

        if product is None:
            raise ProductNotFoundError(
                f"Product with ID {product_id} was not found."
            )

        update_data = product_data.model_dump(
            exclude_unset=True,
        )

        new_sku = update_data.get("sku")

        if new_sku is not None and new_sku != product.sku:
            existing_product = self.repository.get_by_sku(
                db,
                new_sku,
            )

            if existing_product is not None:
                raise ProductAlreadyExistsError(
                    f"Product with SKU '{new_sku}' already exists."
                )

        for field, value in update_data.items():
            setattr(product, field, value)

        try:
            db.commit()
            db.refresh(product)
        except Exception:
            db.rollback()
            raise

        return product

    def delete_product(
        self,
        db: Session,
        product_id: int,
    ) -> None:
        product = self.repository.get_by_id(
            db,
            product_id,
        )

        if product is None:
            raise ProductNotFoundError(
                f"Product with ID {product_id} was not found."
            )

        try:
            self.repository.delete(
                db,
                product,
            )
            db.commit()
        except Exception:
            db.rollback()
            raise