import json

from odoo import http
from odoo.http import request

from odoo.addons.sale.controllers.product_configurator import (
    ProductConfiguratorController,
)


class WebSiteSale(ProductConfiguratorController):
    @http.route(
        ['/shop/product/<model("product.template"):product>'],
        type="http",
        auth="public",
        website=True,
    )
    def product(self, product, category="", search="", **kwargs):
        response = super(WebSiteSale, self).product(
            product, category="", search="", **kwargs
        )
        response.qcontext["domain"] = request.httprequest.args.get("domain") or ""
        return response

    @http.route(
        ["/shop/cart/update"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        form = http.request.httprequest.form
        context = request.context.copy()

        if "domain" in form:
            if form["domain"] != "":
                context.update(domain=form["domain"])

        # This route is called when adding a product to cart (no options).
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != "draft":
            request.session["sale_order_id"] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get("product_custom_attribute_values"):
            product_custom_attribute_values = json.loads(
                kw.get("product_custom_attribute_values")
            )

        no_variant_attribute_values = None
        if kw.get("no_variant_attribute_values"):
            no_variant_attribute_values = json.loads(
                kw.get("no_variant_attribute_values")
            )

        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values,
            context=context,
        )
        return request.redirect("/shop/cart")
