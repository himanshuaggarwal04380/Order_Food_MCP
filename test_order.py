from decimal import Decimal
import pytest

from order import place_order, OrderLineItem, OrderError


def test_reference_order_case():
    """
    Documented reference test case (see README):
    2x Margherita Pizza (PZ01, Rs.249) + 1x Masala Chai (HB10, Rs.89)
    Subtotal: 587.00 | Tax (8%): 46.96 | Delivery: 100 | Total: 733.96
    Hand-verified.
    """
    invoice = place_order([
        OrderLineItem(item_id="PZ01", quantity=2),
        OrderLineItem(item_id="HB10", quantity=1),
    ])

    assert invoice.subtotal == Decimal("587.00")
    assert invoice.tax_amount == Decimal("46.96")
    assert invoice.delivery_fee == Decimal("100")
    assert invoice.total == Decimal("733.96")
    assert len(invoice.lines) == 2


def test_order_with_unknown_item_raises():
    with pytest.raises(OrderError):
        place_order([OrderLineItem(item_id="does-not-exist", quantity=1)])


def test_order_with_zero_quantity_raises():
    with pytest.raises(OrderError):
        place_order([OrderLineItem(item_id="PZ01", quantity=0)])


def test_order_with_negative_quantity_raises():
    with pytest.raises(OrderError):
        place_order([OrderLineItem(item_id="PZ01", quantity=-2)])


def test_empty_order_raises():
    with pytest.raises(OrderError):
        place_order([])


def test_order_id_is_unique_across_orders():
    inv1 = place_order([OrderLineItem(item_id="PZ01", quantity=1)])
    inv2 = place_order([OrderLineItem(item_id="PZ01", quantity=1)])
    assert inv1.order_id != inv2.order_id