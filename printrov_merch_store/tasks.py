import frappe

from printrov_merch_store.utils import make_printrove_request


@frappe.whitelist()
def sync_products_from_printrove():
    # if not synced, sync categories first
    categories_are_synced = frappe.db.get_single_value(
        "Printrove Settings", "categories_synced"
    )

    if not categories_are_synced:
        sync_categories_from_printrove()
        frappe.db.set_single_value(
            "Printrove Settings", "categories_synced", 1
        )

    products_route = "api/external/products"
    all_products = make_printrove_request(products_route)
    all_products = all_products["products"]

    for product in all_products:
        variants = get_product_variants(product["id"])

        product_data = {
            "front_mockup": product["mockup"]["front_mockup"],
            "back_mockup": product["mockup"]["back_mockup"],
            "printrove_category": product["product"]["name"],
            "printrove_category_id": product["product"]["id"],
            "variants": variants,
        }

        if not frappe.db.exists(
            "Store Product", {"printrove_id": product["id"]}
        ):
            doc = frappe.get_doc(
                {
                    "doctype": "Store Product",
                    "name": product["name"],
                    "printrove_id": product["id"],
                    **product_data,
                }
            ).insert(ignore_permissions=True)
        else:
            # update the product
            doc = frappe.get_doc(
                "Store Product", {"printrove_id": product["id"]}
            )
            doc.update({**product_data})
            doc.save(ignore_permissions=True)


def get_product_variants(product_id):
    product_details_endpoint = f"api/external/products/{product_id}"
    product_details = make_printrove_request(product_details_endpoint)

    variants = product_details["product"]["variants"]

    # process variants
    processed_variants = []
    for variant in variants:
        processed_variants.append(
            {
                "variant_id": variant["id"],
                "sku": variant["sku"],
                "variant_name": variant["product"]["name"],
                "color": variant["product"]["color"],
                "size": variant["product"]["size"],
            }
        )

    return processed_variants


def sync_order_status_from_printrove():
    orders_to_sync = frappe.db.get_all(
        "Store Order",
        filters={
            "status": ("not in", ("Paid", "Cancelled", "Delivered")),
            "printrove_order_id": ("!=", ""),
        },
        pluck="printrove_order_id",
    )

    for order_id in orders_to_sync:
        try:
            sync_status_for_order(order_id)
        except:
            frappe.log_error(
                "Error syncing order",
                f"Printrove Order ID: {order_id}",
            )


def sync_status_for_order(order_id):
    order_endpoint = f"api/external/orders/{order_id}"
    response = make_printrove_request(order_endpoint)
    status = response["order"]["status"]

    order = frappe.get_doc(
        "Store Order", {"printrove_order_id": order_id}
    )
    order.printrove_status = status
    if status in ("Cancelled", "Delivered"):
        order.status = status

    order.save(ignore_permissions=True)

    if status == "Cancelled" and order.docstatus != 2:
        order.cancel()


def sync_categories_from_printrove():
    endpoint = "api/external/categories"
    response = make_printrove_request(endpoint)
    categories = response["categories"]

    for category in categories:
        frappe.get_doc(
            {
                "doctype": "Printrove Category",
                "name": category["name"],
                "id": category["id"],
            }
        ).insert(ignore_permissions=True, ignore_if_duplicate=True)
