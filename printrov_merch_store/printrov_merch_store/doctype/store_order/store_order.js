// Copyright (c) 2023, Build With Hussain and contributors
// For license information, please see license.txt

frappe.ui.form.on("Store Order", {
  refresh(frm) {
    if (frm.doc.status == "Paid") {
      frm.add_custom_button(__("Place Order on Printrove"), () => {
        frm
          .call({
            doc: frm.doc,
            method: "place_order_on_printrove",
            freeze: true
          })
          .then(() => {
            frappe.msgprint("Order Placed on Printrove")
          });
      }, "Actions");


    }

    const btn = frm.add_custom_button("Sync Order Status", () => {
      frm.call({
        doc: frm.doc,
        method: "sync_status_from_printrove",
        btn
      }).then(() => {
        frappe.msgprint("Order Status Synced")
        frm.reload();
      });
    }, "Actions");
  },
});
