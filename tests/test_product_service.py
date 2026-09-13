from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import (
    ProductAlreadyExistsError,
    ProductNotFoundError,
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


def test_get_product_by_id_not_found():
    repository = Mock(spec=ProductRepository)
    repository.get_by_id.return_value = None

    service = ProductService(repository)
    db = Mock()

    with pytest.raises(ProductNotFoundError):
        service.get_product_by_id(db, 999)

    repository.get_by_id.assert_called_once_with(db, 999)


def test_update_product_success():
    repository = Mock(spec=ProductRepository)

    existing_product = Product(
        sku="CHAIR-001",
        name="Office Chair",
        category="Chair",
        price=Decimal("249.99"),
    )

    repository.get_by_id.return_value = existing_product

    service = ProductService(repository)
    db = Mock()

    product_data = ProductUpdate(
        category="Office Furniture",
        price=Decimal("219.99"),
    )

    result = service.update_product(
        db,
        1,
        product_data,
    )

    repository.get_by_id.assert_called_once_with(db, 1)

    assert result.category == "Office Furniture"
    assert result.price == Decimal("219.99")

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(existing_product)


def test_update_product_rejects_duplicate_sku():
    repository = Mock(spec=ProductRepository)

    existing_product = Product(
        sku="CHAIR-001",
        name="Office Chair",
        price=Decimal("249.99"),
    )

    duplicate_product = Product(
        sku="CHAIR-002",
        name="Another Chair",
        price=Decimal("199.99"),
    )

    repository.get_by_id.return_value = existing_product
    repository.get_by_sku.return_value = duplicate_product

    service = ProductService(repository)
    db = Mock()

    product_data = ProductUpdate(
        sku="CHAIR-002",
    )

    with pytest.raises(ProductAlreadyExistsError):
        service.update_product(
            db,
            1,
            product_data,
        )

    repository.get_by_sku.assert_called_once_with(
        db,
        "CHAIR-002",
    )

    db.commit.assert_not_called()


def test_delete_product_success():
    repository = Mock(spec=ProductRepository)

    existing_product = Product(
        sku="CHAIR-001",
        name="Office Chair",
        price=Decimal("249.99"),
    )

    repository.get_by_id.return_value = existing_product

    service = ProductService(repository)
    db = Mock()

    service.delete_product(
        db,
        1,
    )

    repository.get_by_id.assert_called_once_with(db, 1)
    repository.delete.assert_called_once_with(
        db,
        existing_product,
    )

    db.commit.assert_called_once()


def test_delete_product_not_found():
    repository = Mock(spec=ProductRepository)
    repository.get_by_id.return_value = None

    service = ProductService(repository)
    db = Mock()

    with pytest.raises(ProductNotFoundError):
        service.delete_product(
            db,
            999,
        )

    repository.delete.assert_not_called()
    db.commit.assert_not_called()