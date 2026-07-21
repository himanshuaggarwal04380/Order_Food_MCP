from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from datetime import date

from menu import get_item_by_id


TAX_RATE = Decimal("0.08")
DELIVERY_FEE = Decimal("100")


@dataclass
class OrderLineItem:
    """One line in an incoming order request: an item ID and how many."""
    item_id: str
    quantity: int


@dataclass
class InvoiceLine:
    """One priced, resolved line in the final invoice."""
    name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


@dataclass
class Invoice:
    """The full structured result of placing an order."""
    order_id: str
    order_date: date
    lines: list[InvoiceLine]
    subtotal: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    delivery_fee: Decimal
    total: Decimal


class OrderError(Exception):
    """Raised when an order cannot be placed due to invalid input."""
    pass


def place_order(line_items: list[OrderLineItem]) -> Invoice:
    """
    Validate and price an order, returning a full Invoice.
    Raises OrderError with a clear message if the order is invalid.
    """
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
                name=menu_item.name,
                quantity=line.quantity,
                unit_price=menu_item.price,
                line_total=line_total,
            )
        )

    subtotal = sum((l.line_total for l in invoice_lines), start=Decimal("0.00"))
    tax_amount = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
    total = subtotal + tax_amount + DELIVERY_FEE
    today = datetime.now().strftime("%Y%m%d")   # 20260720
    order_number = 1
    
    

    return Invoice(
        order_id=f"{today}-{order_number:03d}",
        order_date=date.today(),
        lines=invoice_lines,
        subtotal=subtotal,
        tax_rate=TAX_RATE,
        tax_amount=tax_amount,
        delivery_fee=DELIVERY_FEE,
        total=total,
    )