from odoo import _, fields, models


class SgwWhoisTld(models.Model):
    _name = "sgw.whois.tld"
    _order = "tld"
    _description = "TLDs"
    _rec_name = "tld"
    _sql_constraints = [("tld", "unique (tld)", _("TLD must be unique."))]

    tld = fields.Char("TLD", required=True,)
    type_tld = fields.Selection(
        [("cc", "Country Code"), ("gtld", "Generic TLD")], "Type TLD", default="gtld"
    )
    notes = fields.Text("Notes")
    whois_server = fields.Many2one("sgw.whois.server", ondelete="set null")
