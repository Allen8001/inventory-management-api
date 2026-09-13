from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate
from app.services.product_service import (
    ProductAlreadyExistsError,
    ProductService,
)


def test_create_product_rejects_duplicate_sku():
    repository = Mock(spec=ProductRepository)

    repository.get_by_sku.return_value = Product(
        sku="CHAIR-001",
        name="Existing Chair",
        price="199.99",
    )

    service = ProductService(repository)
    db = Mock()

    product_data = ProductCreate(
        sku="CHAIR-001",
        name="Office Chair",
        price="249.99",
    )

    with pytest.raises(ProductAlreadyExistsError):
        service.create_product(db, product_data)

    repository.add.assert_not_called()
    db.commit.assert_not_called()


def test_create_product_success():
    repository = Mock(spec=ProductRepository)
    repository.get_by_sku.return_value = None

    service = ProductService(repository)
    db = Mock()

    product_data = ProductCreate(
        sku="CHAIR-001",
        name="Office Chair",
        description="Ergonomic office chair",
        category="Chair",
        price="249.99",
    )

    result = service.create_product(db, product_data)

    repository.get_by_sku.assert_called_once_with(
        db,
        "CHAIR-001",
    )

    repository.add.assert_called_once()

    saved_product = repository.add.call_args.args[1]

    assert saved_product.sku == "CHAIR-001"
    assert saved_product.name == "Office Chair"
    assert saved_product.price == Decimal("249.99")

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(saved_product)

    assert result is saved_product