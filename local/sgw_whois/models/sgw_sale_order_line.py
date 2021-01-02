from odoo import fields, models


class SgwSaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    domain_name = fields.Char("Domain Name")
