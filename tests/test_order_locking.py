import os
import threading
from decimal import Decimal

import pytest

from app import crud, models, schemas
from app import database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


TEST_DB_URL = os.environ.get("TEST_DATABASE_URL")


pytestmark = pytest.mark.skipif(not TEST_DB_URL, reason="Set TEST_DATABASE_URL to run DB integration tests")


def _rebind_database(test_db_url: str):
    # Rebind the app database engine/session to the test DB
    database.engine = create_engine(test_db_url)
    database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database.engine)
    # Ensure tables exist
    database.Base.metadata.create_all(bind=database.engine)


def _cleanup_all():
    db = database.SessionLocal()
    try:
        # Delete in dependency order
        db.query(models.OrderTracking).delete()
        db.query(models.Payment).delete()
        db.query(models.Order).delete()
        db.query(models.ShoppingCartItem).delete()
        db.query(models.ShoppingCart).delete()
        db.query(models.Inventory).delete()
        db.query(models.Product).delete()
        db.query(models.Address).delete()
        db.query(models.Review).delete()
        db.query(models.CustomerSession).delete()
        db.query(models.User).delete()
        db.commit()
    finally:
        db.close()


def setup_module(module):
    # Prepare test DB binding
    _rebind_database(TEST_DB_URL)
    _cleanup_all()


def teardown_module(module):
    _cleanup_all()


def create_user(db, username="testuser"):
    u = models.User(username=username, password_hash="x", email=f"{username}@example.com")
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def create_product_and_inventory(db, sku="SKU1", qty=5, price=Decimal("10.00")):
    p = models.Product(sku=sku, name="Prod", price=price)
    db.add(p)
    db.commit()
    db.refresh(p)

    inv = models.Inventory(product_id=p.id, quantity_in_stock=qty, reorder_level=1)
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # attach relation and return
    p.inventory = inv
    db.commit()
    db.refresh(p)
    return p, inv


def create_cart_with_item(db, user_id, product_id, quantity=1):
    cart = models.ShoppingCart(user_id=user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)

    item = models.ShoppingCartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return cart, item


def test_single_order_decrements_and_clears_cart():
    db = database.SessionLocal()
    try:
        user = create_user(db, "single_user")
        product, inventory = create_product_and_inventory(db, sku="SKU_SINGLE", qty=3)
        cart, item = create_cart_with_item(db, user.id, product.id, quantity=2)

        order_in = schemas.OrderCreate(cart_id=cart.id, address="123 Test St")
        db_order = crud.create_order(db, user.id, order_in)
        # After order, inventory should be decremented
        db.refresh(inventory)
        assert int(inventory.quantity_in_stock) == 1

        # Cart should be cleared (no items)
        refreshed_cart = db.query(models.ShoppingCart).get(cart.id)
        assert len(refreshed_cart.items) == 0
    finally:
        db.close()


def _attempt_order(result_list, user_name, product_id, quantity=1):
    db = database.SessionLocal()
    try:
        user = create_user(db, user_name)
        cart, _ = create_cart_with_item(db, user.id, product_id, quantity=quantity)
        try:
            order_in = schemas.OrderCreate(cart_id=cart.id, address="Addr")
            ord = crud.create_order(db, user.id, order_in)
            result_list.append((user_name, True, ord.id))
        except Exception as e:
            result_list.append((user_name, False, str(e)))
    finally:
        db.close()


def test_concurrent_orders_do_not_oversell():
    # Product with qty=1, two users concurrently ordering qty=1 each should result
    # in exactly one success and one failure.
    db = database.SessionLocal()
    try:
        p, inv = create_product_and_inventory(db, sku="SKU_CONC", qty=1)
    finally:
        db.close()

    results = []
    t1 = threading.Thread(target=_attempt_order, args=(results, "u_conc_1", p.id, 1))
    t2 = threading.Thread(target=_attempt_order, args=(results, "u_conc_2", p.id, 1))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Exactly one succeeded
    successes = [r for r in results if r[1] is True]
    failures = [r for r in results if r[1] is False]
    assert len(successes) == 1
    assert len(failures) == 1
    # Confirm inventory now zero (product has no quantity column)
    db2 = database.SessionLocal()
    try:
        inv2 = db2.query(models.Inventory).filter(models.Inventory.product_id == p.id).first()
        assert int(inv2.quantity_in_stock) == 0
    finally:
        db2.close()
