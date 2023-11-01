import frappe
from razorpay.errors import (
    SignatureVerificationError as RazorpaySignatureVerificationError,
)

from printrov_merch_store.utils import (
    get_available_couriers,
    get_razorpay_client,
)


@frappe.whitelist()
def handle_checkout_submit(product_name: str, order_details):
    order_details = frappe.parse_json(order_details)

    validate_serviceability(order_details.get("pincode"))

    # Get the razorpay client
    razorpay_client = get_razorpay_client()
    retail_price = frappe.db.get_value(
        "Store Product", product_name, "retail_price"
    )

    razorpay_order = razorpay_client.order.create(
        {
            "amount": retail_price * 100,
            "currency": "INR",
        }
    )

    create_store_order(product_name, order_details, razorpay_order)

    return {
        "key_id": razorpay_client.auth[0],
        "order_id": razorpay_order["id"],
    }
    # print(order_details)


def validate_serviceability(pincode):
    couriers = []
    try:
        couriers = get_available_couriers(pincode)
    except Exception:
        frappe.throw("Sorry, we don't deliver to your location yet.")

    if not couriers:
        frappe.throw("Sorry, we don't deliver to your location yet.")


@frappe.whitelist()
def handle_payment_success(order_id, payment_id, signature):
    razorpay_client = get_razorpay_client()
    try:
        razorpay_client.utility.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )
    except RazorpaySignatureVerificationError:
        frappe.throw("Invalid Payment Signature")

    so = frappe.get_doc(
        "Store Order", {"razorpay_order_id": order_id}
    )
    so.update(
        {
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
            "status": "Paid",
        }
    )
    so.save()

    return so.name


def create_store_order(product_name, order_details, razorpay_order):
    couriers = get_available_couriers(order_details.get("pincode"))

    # select the cheapest (for now)
    cheapest_courier = min(couriers, key=lambda x: x["cost"])

    order = frappe.new_doc("Store Order")
    order.product = product_name
    order.variant_id = order_details.variant_id
    order.user = frappe.session.user
    order.update(
        {
            "customer_name": order_details.customer_name,
            "phone_number": order_details.phone_number,
            "address_line_1": order_details.address_line_1,
            "address_line_2": order_details.address_line_2,
            "address_line_3": order_details.address_line_3,
            "city": order_details.city,
            "state": order_details.state,
            "pincode": order_details.pincode,
            "country": "India",  # todo: later, international shipping!
            "razorpay_order_id": razorpay_order["id"],
            "courier_id": cheapest_courier["id"],
            "courier_name": cheapest_courier["name"],
            "courier_cost_inr": cheapest_courier["cost"],
        }
    )
    return order.insert()
