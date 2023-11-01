// Copyright (c) 2023, Build With Hussain and contributors
// For license information, please see license.txt

frappe.ui.form.on("Store Product", {
  refresh(frm) {
    const button_label = frm.doc.is_published ? __("Unpublish") : __("Publish");

    frm.add_custom_button(button_label, () => {
      frm.set_value("is_published", !frm.doc.is_published);
      frm.save();
    });
  },
});
