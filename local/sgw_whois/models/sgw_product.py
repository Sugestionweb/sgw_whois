# -*- coding: utf-8 -*-

from odoo import models, fields


class sgw_products(models.Model):
    _inherit = 'product.template'

    is_tld = fields.Boolean(
        'Is TLD', 
        help="Select this option if this product is a domain TLD or TLD Group."
        )

    list_tlds = fields.Char(
        'TLDs', 
        help="Specify the TLDs to which this product refers separated by ',' "
        )
