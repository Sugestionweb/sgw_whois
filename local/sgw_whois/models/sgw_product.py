# -*- coding: utf-8 -*-

from openerp import models, fields

class sgw_products(models.Model):
    _inherit = 'product.template'
    is_tld = fields.Boolean('Is TLD')
    list_tlds = fields.Char('TLDs')
