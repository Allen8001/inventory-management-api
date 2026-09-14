from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:

    def get_by_id(
        self,
        db: Session,
        product_id: int,
    ) -> Product | None:
        return db.get(
            Product,
            product_id,
        )

    def get_by_sku(
        self,
        db: Session,
        sku: str,
    ) -> Product | None:
        statement = select(Product).where(
            Product.sku == sku
        )

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        statement = (
            select(Product)
            .order_by(Product.id)
            .offset(offset)
            .limit(limit)
        )

        return list(
        db.scalars(statement).all()
    )

    def add(
        self,
        db: Session,
        product: Product,
    ) -> Product:
        db.add(product)
        db.flush()

        return product

    def delete(
        self,
        db: Session,
        product: Product,
    ) -> None:
        db.delete(product)
        db.flush()