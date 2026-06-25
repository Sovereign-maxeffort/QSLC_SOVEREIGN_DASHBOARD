import os
try:
    import stripe
except Exception:
    stripe = None


def init_stripe():
    key = os.getenv("STRIPE_API_KEY")
    if not key:
        raise EnvironmentError("STRIPE_API_KEY environment variable not set")
    if stripe is None:
        raise ImportError("stripe library is not installed; add it to requirements.txt and install")
    stripe.api_key = key
    return stripe


def create_product_and_checkout(product_name, amount_cents, currency='usd', success_url=None, cancel_url=None):
    s = init_stripe()

    # Find existing product by name
    product = None
    for p in s.Product.list(limit=100).auto_paging_iter():
        if p.name == product_name:
            product = p
            break

    if not product:
        product = s.Product.create(name=product_name)

    price = s.Price.create(unit_amount=amount_cents, currency=currency, product=product.id)

    session = s.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price.id, "quantity": 1}],
        mode="payment",
        success_url=success_url or "https://example.com/success",
        cancel_url=cancel_url or "https://example.com/cancel",
    )

    return session
