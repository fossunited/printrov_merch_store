// Copyright (c) 2023, Build With Hussain and contributors
// For license information, please see license.txt

frappe.ui.form.on("Printrove Settings", {
  refresh(frm) {
    const btn = frm.add_custom_button("Sync Products Now", () => {
      frappe
        .call({
          method: "printrov_merch_store.tasks.sync_products_from_printrove",
          btn,
        })
        .then(() => {
          frappe.show_alert({ message: "Store Products Synced Successfully!", indicator: "green" });
        });
    });

    frm.set_query("default_order_invoice_format", (doc) => {
      return {
        filters: {
          doc_type: "Store Order"
        }
      }
    })
  },
});
