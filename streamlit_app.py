import os
import streamlit as st

from visuals import render_holographic
import stripe_utils

st.set_page_config(page_title="QSLC Sovereign Dashboard", layout="wide")

st.title("QSLC Sovereign — Access & Tiers")

st.markdown("""
Welcome to the QSLC Sovereign access dashboard. Use the controls below to preview holographic visuals
and create Stripe products / checkout sessions for access tiers.

Notes: set the environment variable `STRIPE_API_KEY` before creating products.
""")

col1, col2 = st.columns([2, 1])

with col1:
    render_holographic()

with col2:
    st.header("Access Tiers")

    # Define five tiers (amounts are in USD cents by default)
    tiers = [
        {"name": "Tier 1 — Bronze", "amount": 10_000, "description": "Entry access"},
        {"name": "Tier 2 — Silver", "amount": 50_000, "description": "Expanded access"},
        {"name": "Tier 3 — Gold", "amount": 100_000, "description": "Priority access"},
        {"name": "Tier 4 — Platinum", "amount": 500_000, "description": "Enterprise access"},
        {"name": "Tier 5 — Sovereign", "amount": 1_000_000, "description": "Full sovereign access"},
    ]

    for t in tiers:
        st.subheader(t["name"])
        st.write(t["description"])
        st.write(f"Price: ${t['amount']/100:,.2f}")

        if st.button(f"Create checkout for {t['name']}", key=t['name']):
            try:
                session = stripe_utils.create_product_and_checkout(
                    product_name=t['name'], amount_cents=t['amount'], currency='usd',
                    success_url=os.getenv('SUCCESS_URL', 'https://example.com/success'),
                    cancel_url=os.getenv('CANCEL_URL', 'https://example.com/cancel')
                )
                st.success("Checkout session created")
                st.write(session.url)
            except Exception as e:
                st.error(f"Stripe error: {e}")

    st.markdown("---")
    st.write("Tip: set `STRIPE_API_KEY` as an env var and try again.")
