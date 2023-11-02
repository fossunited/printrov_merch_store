import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = (
            f"/login?redirect-to={frappe.request.url}"
        )
        raise frappe.Redirect
