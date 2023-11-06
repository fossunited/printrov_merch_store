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

            printrove_settings = frappe.get_cached_doc(
                "Printrove Settings"
            )
            if printrove_settings.send_invoice_on_order:
                self.send_invoice_to_customer()

    @frappe.whitelist()
    def place_order_on_printrove(self):
        try:
            self._place_order_on_printrove()
        except Exception as e:
            frappe.log_error(
                frappe.get_traceback(),
                f"Error while placing order {self.name} on Printrove",
            )
            frappe.throw("Something went wrong!")

    def _place_order_on_printrove(self):
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
        self.submit()

    def send_invoice_to_customer(self):
        printrove_settings = frappe.get_cached_doc(
            "Printrove Settings"
        )
        invoice_attachment = frappe.attach_print(
            self.doctype,
            self.name,
            file_name=self.name,
            print_format=printrove_settings.order_invoice_format,
        )

        attachments = [invoice_attachment]
        message = f"Here is your invoice for order {self.name}"

        if (
            printrove_settings.invoice_email_message
            and printrove_settings.invoice_email_message != ""
        ):
            message = frappe.render_template(
                printrove_settings.invoice_email_message,
                {"order": self},
            )

        frappe.sendmail(
            recipients=self.user,
            subject=f"Order placed successfully {self.name}",
            content=message,
            attachments=attachments,
        )

        self.db_set("invoice_sent_via_email", 1)

    @frappe.whitelist()
    def sync_status_from_printrove(self):
        sync_status_for_order(self.printrove_order_id)
        self.reload()
