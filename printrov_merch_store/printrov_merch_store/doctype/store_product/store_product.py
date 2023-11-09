# Copyright (c) 2023, Build With Hussain and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class StoreProduct(WebsiteGenerator):
    @property
    def has_sizes(self):
        return any(v.size for v in self.variants)

    @property
    def has_colors(self):
        return any(v.color for v in self.variants)

    def get_context(self, context):
        context.add_breadcrumbs = 1
        context.parents = [
            {"label": "Store", "route": "/store"},
            {
                "label": self.printrove_category,
                "route": "/store?category=" + self.printrove_category,
            },
        ]
        settings = frappe.get_cached_doc("Printrove Settings")

        if settings.use_custom_product_view_template:
            custom_rendered_html = frappe.render_template(
                settings.custom_product_view_template, {"doc": self}
            )

            context.custom_rendered_html = custom_rendered_html

        context.has_sizes = self.has_sizes
        context.has_colors = self.has_colors
        context.render_variants = not (
            context.has_sizes or context.has_colors
        ) and len(self.variants) > 1

        meta_image = (
            self.meta_image or self.front_mockup or self.back_mockup
        )
        context.metatags = {
            "title": self.get_title(),
            "image": meta_image,
            "description": self.meta_description or self.get_title(),
            "keywords": f"{self.printrove_category},{self.name}",
        }
