from odoo import fields, models


class SgwWhoisg_Tld(models.Model):
    _name = "sgw.whoisg_tld"
    _order = "gtld desc"
    _description = "Country Codes TLD"

    gtld = fields.Char("gTLD", required=True)
    whois_server = fields.Char("Whois server", required=True)
    notes = fields.Text("Notes")
