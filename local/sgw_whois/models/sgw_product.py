from odoo import fields, models


class SgwProducts(models.Model):
    _inherit = "product.template"

    is_tld = fields.Boolean(
        "Is TLD",
        help="Select this option if this product is a domain TLD or TLD Group.",
    )

    list_tlds = fields.Char(
        "TLDs", help="Specify the TLDs to which this product refers separated by ',' "
    )
