from decimal import Decimal

from receipt_sender import StreamingPayment, generate_receipt


def main() -> None:
    payment = StreamingPayment(
        payment_id="pay_demo_20260907_001",
        creator="Mina Chen",
        listener="Alex Rivera",
        title="Night Train (single stream)",
        amount=Decimal("4.50"),
    )
    result = generate_receipt(payment)
    print(result["data"])


if __name__ == "__main__":
    main()

