import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = (
            f"/login?redirect-to={frappe.request.url}"
        )
        raise frappe.Redirect

    success_page_route = "/store/success"
    printrove_settings = frappe.get_cached_doc("Printrove Settings")
    if printrove_settings.override_success_page:
        success_page_route = printrove_settings.success_page_route

    context.success_page_route = success_page_route
