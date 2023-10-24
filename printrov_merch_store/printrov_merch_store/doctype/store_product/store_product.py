# Copyright (c) 2023, Build With Hussain and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class StoreProduct(WebsiteGenerator):
	def get_context(self, context):
		settings = frappe.get_cached_doc("Printrove Settings")

		if settings.use_custom_product_view_template:
			custom_rendered_html = frappe.render_template(
				settings.custom_product_view_template, 
				{"doc": self}
			)

			context.custom_rendered_html = custom_rendered_html


