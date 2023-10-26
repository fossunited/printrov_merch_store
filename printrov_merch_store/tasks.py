import frappe

from printrov_merch_store.utils import make_printrove_request


@frappe.whitelist()
def sync_products_from_printrove():
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
