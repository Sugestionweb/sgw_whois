from odoo import fields, models


class sgw_sale_order_line(models.Model):
    _inherit = "sale.order.line"
    domain_name = fields.Char("Domain Name")
