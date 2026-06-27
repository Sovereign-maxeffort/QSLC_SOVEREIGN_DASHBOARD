import pandas as pd
import streamlit as st

st.set_page_config(page_title="Base44 Sales Control", page_icon="🚀", layout="wide")

st.title("🚀 Base44 / Sellable Apps Control")
st.caption("QSLC EVE rule: no app is sellable until it has a product row, price rule, destination account, and logging lane.")

st.markdown("""
<style>
.stApp { background: #020617; color: #e0fbff; }
.card { border: 1px solid rgba(0,243,255,.25); background: rgba(15,23,42,.7); padding: 18px; border-radius: 16px; }
</style>
""", unsafe_allow_html=True)

plans = pd.DataFrame([
    {"plan": "Free", "use": "Testing only", "production": "No"},
    {"plan": "Starter", "use": "Tiny MVP", "production": "Limited"},
    {"plan": "Builder", "use": "Real app + custom domain + export", "production": "Recommended start"},
    {"plan": "Pro", "use": "Growing usage", "production": "Yes"},
    {"plan": "Elite", "use": "High-volume commercial", "production": "Yes"},
])

st.subheader("Plan decision")
st.dataframe(plans, use_container_width=True)
st.success("Use Builder or higher for anything you plan to sell.")

st.subheader("Sellable product rows")
products = pd.DataFrame([
    {
        "product_id": "prod_eve_ops",
        "name": "QSLC EVE Operations App",
        "base_price_cents": 4000,
        "billing_model": "monthly",
        "linked_app_id": "base44_app_id_here",
        "destination_account_id": "acct_primary",
        "status": "sellable",
    },
    {
        "product_id": "prod_doc_packet",
        "name": "Document Generation Packet",
        "base_price_cents": 2500,
        "billing_model": "one_time",
        "linked_app_id": "base44_app_id_here",
        "destination_account_id": "acct_primary",
        "status": "draft",
    },
    {
        "product_id": "prod_payroll_export",
        "name": "Payroll Export Service",
        "base_price_cents": 1500,
        "billing_model": "per_use",
        "linked_app_id": "base44_app_id_here",
        "destination_account_id": "acct_primary",
        "status": "draft",
    },
])
st.dataframe(products, use_container_width=True)
st.download_button("Download products template CSV", products.to_csv(index=False), "base44_products_template.csv", "text/csv")

st.subheader("Backend endpoints")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### `/pricing/quote`")
    st.code('{"product_id":"prod_eve_ops","user_id":"user_001","appointment_id":"appt_001"}', language="json")
with col2:
    st.markdown("### `/payments/create`")
    st.code('{"product_id":"prod_eve_ops","user_id":"user_001","appointment_id":"appt_001","payment_provider":"stripe"}', language="json")
with col3:
    st.markdown("### `/docs/generate`")
    st.code('{"template_id":"court_doc_packet","user_id":"user_001","case_id":"case_001"}', language="json")

st.subheader("Agent routing rule")
st.markdown("""
1. User books an appointment.
2. Appointment has `service_id`.
3. `service_id` maps to `product_id`.
4. Product row supplies price and destination account.
5. Backend calculates exact amount.
6. Payment provider collects funds.
7. Result logs back to QSLC SSOT.

**No product row = do not sell.**
""")

st.warning("Do not commit live Stripe, PayPal, bank, Base44, Groq, ElevenLabs, OpenAI, or GitHub secrets to this repo.")
