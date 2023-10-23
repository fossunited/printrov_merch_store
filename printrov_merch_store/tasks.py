import frappe

from frappe.integrations.utils import make_get_request, make_post_request


BASE_URL = "https://api.printrove.com/"

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
            "back_mockup": product["mockup"]["back_mockup"]
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
    printrove_settings = frappe.get_single("Printrove Settings")
    auth_route = "api/external/token"
    response = make_post_request(
        f"{BASE_URL}{auth_route}",
        data={
            "email": printrove_settings.email,
            "password": printrove_settings.get_password("password"),
        },
    )
    return response["access_token"]
