frappe.listview_settings["Store Order"] = {
    get_indicator: (doc) => {
      let status_color_map = {
        "Payment Pending": "gray",
        "Paid": "green",
        "Placed On Printrove": "cyan",
        "Delivered": "pink"
      };

      return [doc.status, status_color_map[doc.status], "status,=," + doc.status];
    },
};
