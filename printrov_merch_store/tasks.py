import frappe

from frappe.integrations.utils import make_get_request, make_post_request


BASE_URL = "https://api.printrove.com/"
SECONDS_IN_YEAR = 364 * 24 * 60 * 60

@frappe.whitelist()
def sync_products_from_printrove():
    access_token = get_printrove_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    products_route = "api/external/products"
    all_products = make_get_request(f"{BASE_URL}{products_route}", headers=headers)
    all_products = all_products["products"]

    for product in all_products:
        product_data = {
            "front_mockup": product["mockup"]["front_mockup"],
            "back_mockup": product["mockup"]["back_mockup"],
            "printrove_category": product["product"]["name"],
            "printrove_category_id": product["product"]["id"],
        }

        if not frappe.db.exists("Store Product", {"printrove_id": product["id"]}):
            doc = frappe.get_doc({
                "doctype": "Store Product",
                "name": product["name"],
                "printrove_id": product["id"],
                **product_data
            }).insert(ignore_permissions=True)
        else:
            # update the product
            doc = frappe.get_doc("Store Product", {"printrove_id": product["id"]})
            doc.update({
                **product_data
            })
            doc.save(ignore_permissions=True)

def get_printrove_access_token():
    token = frappe.cache.get_value("printrove_access_token")
    if token:
        return token

    printrove_settings = frappe.get_cached_doc("Printrove Settings")
    auth_route = "api/external/token"
    response = make_post_request(
        f"{BASE_URL}{auth_route}",
        data={
            "email": printrove_settings.email,
            "password": printrove_settings.get_password("password"),
        },
    )

    access_token = response["access_token"]

    # store for a year
    frappe.cache.set_value("printrove_access_token", access_token, expires_in_sec=SECONDS_IN_YEAR)

    return access_token
