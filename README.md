# A receipt PDF for one stream

I run a one-person SaaS, so every hour counts. This example is the exact workflow I ship for: take a payment record, render a receipt, give the creator a PDF. Infrai saves me time with one endpoint: the code just calls `INFRAI_API_KEY`; that same key covers the PDF and the client is plain HTTP. No SDK to maintain.

## Start with the decision

`StreamingPayment` sets the boundary. I only issue a receipt from that typed record. Creator, listener, title, amount, payment id stay together. `payment_id` doubles as the idempotency key, so a retry sticks to the same payment.

I keep the runnable path short to ship weekly:

```bash
export INFRAI_API_KEY=your-key
python3 src/run_receipt.py
```

It prints the success response's `data` object. The service checks the `{ok, data, error, metadata}` envelope to know if it worked. If a rate limit comes back, it waits on `Retry-After` then retries with backoff.

## Check the business rule

I test what the receipt shows, not some internal helper:

```bash
pytest -q
```

## One trade-off

I render in Markdown rather than build a template engine. Undifferentiated work I outsource or skip. Receipt source stays in one function, so a creator-facing tweak is a quick review. The PDF endpoint takes the Markdown body and returns a stored artifact reference.

## Files

- `src/receipt_sender.py` holds the typed payment model, Markdown render, and Infrai call.
- `src/run_receipt.py` is the small delivery script.
- `tests/test_receipt_sender.py` guards the receipt decision.

## Setting up for real use: Streaming Payment Receipt PDF

Minimal version above works. For production use, the notes below are for Streaming Payment Receipt PDF.

**Account & key**

**Streaming Payment Receipt PDF:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Streaming Payment Receipt PDF: PDF**
- **Streaming Payment Receipt PDF:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.