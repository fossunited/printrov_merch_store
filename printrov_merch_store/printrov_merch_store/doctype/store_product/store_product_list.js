frappe.listview_settings["Store Product"] = {
  get_indicator: (doc) => {
    let status = "Not Published";
    let color = "gray";

    if (doc.is_published) {
      status = "Published";
      color = "green";
    }
    return [status, color, "is_published,=," + doc.is_published];
  },
};
