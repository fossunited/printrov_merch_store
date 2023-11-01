# Copyright (c) 2023, Build With Hussain and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from printrov_merch_store.tasks import sync_status_for_order
from printrov_merch_store.utils import make_printrove_request


class StoreOrder(Document):
    def on_update(self):
        if self.has_value_changed("status") and self.status == "Paid":
            frappe.enqueue_doc(
                "Store Order",
                self.name,
                "place_order_on_printrove",
                queue="short",
            )

    @frappe.whitelist()
    def place_order_on_printrove(self):
        order_endpoint = "api/external/orders"

        order_payload = {
            "reference_number": self.name,
            "retail_price": self.retail_price,
            "customer": {
                "name": self.customer_name,
                "email": self.user,
                "number": self.phone_number,
                "address1": self.address_line_1,
                "address2": self.address_line_2,
                "address3": self.address_line_3,
                "city": self.city,
                "state": self.state,
                "country": self.country,
                "pincode": self.pincode,
            },
            "order_products": [
                {
                    "variant_id": self.variant_id,
                    "quantity": 1,  # TODO: later, bulk!
                }
            ],
            "courier_id": self.courier_id,
            "cod": bool(self.cod),
        }

        response = make_printrove_request(
            order_endpoint, method="POST", data=order_payload
        )

        if response["status"] != "success":
            frappe.throw("Something went wrong!")

        printrove_order = response["order"]

        self.update(
            {
                "status": "Placed On Printrove",
                "printrove_order_id": printrove_order["id"],
                "printrove_order_status": printrove_order["status"],
            }
        )
        self.save()

    @frappe.whitelist()
    def sync_status_from_printrove(self):
        sync_status_for_order(self.printrove_order_id)
        self.reload()
