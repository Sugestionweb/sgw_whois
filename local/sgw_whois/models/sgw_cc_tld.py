from odoo import fields, models


class SgwWhoisCC_Tld(models.Model):
    _name = "sgw.whoiscc_tld"
    _order = "cc_tld desc"
    _description = "Country Codes TLD"

    cc_tld = fields.Char("Country Code TLD", required=True)
    notes = fields.Text("Notes")