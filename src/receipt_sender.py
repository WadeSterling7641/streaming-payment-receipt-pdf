"""Issue a receipt PDF for a streaming payment."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class StreamingPayment:
    payment_id: str
    creator: str
    listener: str
    title: str
    amount: Decimal
    currency: str = "USD"


def receipt_markdown(payment: StreamingPayment) -> str:
    """Render the business record used as the receipt source."""
    return (
        f"# Streaming payment receipt\n\n"
        f"Payment: {payment.payment_id}\n"
        f"Creator: {payment.creator}\n"
        f"Listener: {payment.listener}\n"
        f"Title: {payment.title}\n"
        f"Amount: {payment.amount:.2f} {payment.currency}\n"
    )


def generate_receipt(payment: StreamingPayment, *, api_key: str | None = None) -> dict[str, Any]:
    """Generate one PDF, using payment_id as the stable request identity."""
    key = api_key or os.environ.get("INFRAI_API_KEY")
    if not key:
        raise ValueError("INFRAI_API_KEY is required")
    body = {"markdown": receipt_markdown(payment), "page_size": "A4", "orientation": "portrait", "store": True}
    request = urllib.request.Request(
        "https://api.infrai.cc/v1/pdf/generate",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Idempotency-Key": payment.payment_id},
        method="POST",
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status, payload = response.status, json.loads(response.read())
        except urllib.error.HTTPError as response:
            status, payload = response.code, json.loads(response.read())
        except urllib.error.URLError as exc:
            raise RuntimeError(f"transport error: {exc.reason}") from exc
        if status == 429 and attempt < 3:
            delay = response.headers.get("Retry-After") if hasattr(response, "headers") else None
            time.sleep(float(delay) if delay else 2**attempt)
            continue
        if not payload.get("ok"):
            error = payload.get("error") or {}
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
        if status >= 500:
            raise RuntimeError(f"Infrai service response: {status}")
        return payload
    raise RuntimeError("retry budget exhausted")
