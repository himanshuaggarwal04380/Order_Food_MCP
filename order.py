from dataclasses import dataclass
from decimal import Decimal
from datetime import date

from menu import get_item_by_id
from db import generate_order_id, save_order


TAX_RATE = Decimal("0.08")
DELIVERY_FEE = Decimal("100")


@dataclass
class OrderLineItem:
    item_id: str
    quantity: int


@dataclass
class InvoiceLine:
    item_id: str
    name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


@dataclass
class Invoice:
    order_id: str
    order_date: date
    lines: list[InvoiceLine]
    subtotal: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    delivery_fee: Decimal
    total: Decimal


class OrderError(Exception):
    pass


def place_order(line_items: list[OrderLineItem]) -> Invoice:
    if not line_items:
        raise OrderError("Order must contain at least one item.")

    invoice_lines: list[InvoiceLine] = []

    for line in line_items:
        if line.quantity <= 0:
            raise OrderError(
                f"Invalid quantity {line.quantity} for item '{line.item_id}'. "
                "Quantity must be a positive number."
            )

        menu_item = get_item_by_id(line.item_id)
        if menu_item is None:
            raise OrderError(f"Unknown item ID: '{line.item_id}'.")

        line_total = (menu_item.price * line.quantity).quantize(Decimal("0.01"))
        invoice_lines.append(
            InvoiceLine(
                item_id=menu_item.id,
                name=menu_item.name,
                quantity=line.quantity,
                unit_price=menu_item.price,
                line_total=line_total,
            )
        )

    subtotal = sum((l.line_total for l in invoice_lines), start=Decimal("0.00"))
    tax_amount = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
    total = subtotal + tax_amount + DELIVERY_FEE

    today = date.today()
    order_id = generate_order_id(str(today))

    invoice = Invoice(
        order_id=order_id,
        order_date=today,
        lines=invoice_lines,
        subtotal=subtotal,
        tax_rate=TAX_RATE,
        tax_amount=tax_amount,
        delivery_fee=DELIVERY_FEE,
        total=total,
    )

    save_order(invoice)
    return invoice