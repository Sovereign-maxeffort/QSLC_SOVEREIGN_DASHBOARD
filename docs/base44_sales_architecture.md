# QSLC / EVE Base44 Sales Architecture

This document locks the selling architecture into the repo so EVE has one clear product, pricing, appointment, payment, and logging lane.

## Repository target

- GitHub owner / account: `Sovereign-maxeffort`
- Repo: `QSLC_SOVEREIGN_DASHBOARD`
- Canonical app path: `streamlit_app.py`
- Local SSOT path on ROGLEX: `C:\QSLC\SSOT`
- Local vault path on ROGLEX: `C:\QSLC_VAULT`

## Base44 plan decision

For apps intended to sell ASAP, use **Builder or higher**.

- Free: testing only
- Starter: tiny MVP
- Builder: real commercial app, custom domain, GitHub export
- Pro / Elite: growing usage and heavier automation

## Flagship app to sell first

Start with one flagship product, not five loose dashboards.

**Recommended flagship:** QSLC EVE Operations App

Core functions:

1. User login
2. Appointment booking
3. Pricing quote
4. Payment creation
5. Document generation
6. Paychex / timecard export
7. SSOT dashboard logging

## Hard routing rule

EVE does not sell any app unless the SSOT contains:

- Product row
- Price / formula
- Billing model
- Destination account
- Linked app ID
- Logging destination

No product row = do not sell.

## Minimum backend endpoints

### `/pricing/quote`

Input:

```json
{
  "product_id": "prod_eve_ops",
  "user_id": "user_001",
  "appointment_id": "appt_001",
  "quantity": 1
}
```

Output:

```json
{
  "product_id": "prod_eve_ops",
  "amount": 4000,
  "currency": "usd",
  "display_amount": "$40.00",
  "formula_used": "base_price + tax + fees",
  "destination_account_id": "acct_primary"
}
```

### `/payments/create`

Input:

```json
{
  "product_id": "prod_eve_ops",
  "user_id": "user_001",
  "appointment_id": "appt_001",
  "payment_provider": "stripe"
}
```

Backend steps:

1. Look up appointment.
2. Map appointment service to product.
3. Read product price and formula.
4. Read destination account.
5. Create payment session / intent.
6. Log payment to SSOT.
7. Return checkout URL or payment status.

### `/docs/generate`

Input:

```json
{
  "template_id": "court_doc_packet",
  "user_id": "user_001",
  "case_id": "case_001"
}
```

Backend steps:

1. Load template.
2. Validate user data.
3. Generate document.
4. Store PDF path.
5. Log document event to SSOT.

## Appointment flow

1. User books appointment in Base44 app.
2. Appointment is stored in SSOT or backend DB.
3. Appointment has `appointment_id`, `user_id`, `service_id`, and scheduled time.
4. `service_id` maps to `product_id`.
5. Product maps to price and destination account.
6. Payment is created.
7. Payment result is logged.
8. Dashboard updates.

## Data model summary

Primary tables:

- `products`
- `accounts`
- `services`
- `appointments`
- `payments`
- `documents`
- `time_log`
- `audit_log`

## Security rule

Never commit raw API keys, payment keys, bank credentials, or passwords to GitHub.

Use:

- Local `.env` on ROGLEX
- Streamlit Cloud Secrets
- Base44 integration secrets
- Apple Passwords / password manager
- Windows Credential Manager

## Deployment checklist

1. Choose Base44 Builder or higher.
2. Create product rows.
3. Add destination account rows.
4. Add service to product mappings.
5. Wire Base44 buttons:
   - Book & Pay → `/payments/create`
   - Generate Docs → `/docs/generate`
   - Quote → `/pricing/quote`
6. Expose on main site / domain.
7. Log all results back to QSLC SSOT.
