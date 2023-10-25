import frappe
import razorpay


@frappe.whitelist()
def handle_checkout_submit(product_name: str, order_details):
    # Get the razorpay client
    # razorpay_client = get_razorpay_client()

    # razorpay_order = razorpay_client.order.create({
    #     "amount": 100,
    #     "currency": "INR",
    # })
    print(order_details)


def get_razorpay_client():
    razorpay_settings = frappe.get_cached_doc(
        "Printrove Razorpay Settings"
    )
    key_id = razorpay_settings.key_id
    key_secret = razorpay_settings.get_password("key_secret")

    return razorpay.Client(auth=(key_id, key_secret))
