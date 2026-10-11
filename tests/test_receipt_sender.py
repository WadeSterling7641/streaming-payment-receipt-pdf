from decimal import Decimal

from src.receipt_sender import StreamingPayment, receipt_markdown


def test_receipt_records_creator_delivery_and_amount() -> None:
    payment = StreamingPayment("p-17", "Mina Chen", "Alex Rivera", "Night Train", Decimal("4.50"))
    rendered = receipt_markdown(payment)
    assert "Payment: p-17" in rendered
    assert "Creator: Mina Chen" in rendered
    assert "Amount: 4.50 USD" in rendered

